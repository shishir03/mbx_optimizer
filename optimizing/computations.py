import re
import ast
import astor
from collections import Counter
from functools import cmp_to_key

from howBIGisit import how_big_is_it

# Custom parse tree data structure
class ParseTreeNode:
    def __init__(self, ast_parse_tree:ast.BinOp):
        self.op = ast_parse_tree.op

        ast_children = [ast_parse_tree.left, ast_parse_tree.right]
        children = []

        same_op_node = None
        for node in ast_children:
            leaf = isinstance(node, ast.Constant) or isinstance(node, ast.Subscript)
            if not leaf and node.op == self.op:
                same_op_node = node
                break

        while same_op_node:
            same_op_children = same_op_node.children
            ast_children.remove(same_op_node)
            ast_children += same_op_children

            same_op_node = None
            for node in ast_children:
                leaf = isinstance(node, ast.Constant) or isinstance(node, ast.Subscript)
                if not leaf and node.op == self.op:
                    same_op_node = node
                    break

        for node in ast_children:
            if isinstance(node, ast.Subscript):
                # print(ast.dump(parse_tree, indent=4))
                arr = node.value.id
                idx = astor.to_source(node.slice).strip()[1:-1]
                # print(f"{arr}[{idx}]")
                children.append(ParseTreeLeaf(f"{arr}[{idx}]"))
            if isinstance(node, ast.Constant):
                children.append(ParseTreeLeaf(node.value))
            else:
                children.append(ParseTreeNode(node))

        self.children = tuple(sorted(ast_children))
    
    def __str__(self):
        return self.tostring()

    def __lt__(self, other):
        if isinstance(other, ParseTreeLeaf):
            return True

        if(len(self.children)) != len(other.children):
            return len(other.children) < len(self.children)
        
        for i in range(len(self.children)):
            if self.children[i] > other.children[i]:
                return False
            elif self.children[i] < other.children[i]:
                return True

        return False
    
    def __eq__(self, other):
        if not isinstance(other, ParseTreeNode):
            return False
        
        if self.op == other.op and len(self.children) == len(other.children):
            for i in range(len(self.children)):
                if self.children[i] != other.children[i]:
                    return False
                
            return True
        
        return False
    
    def tostring(self, tabdepth=0):
        s = "\t"*tabdepth + f"ParseTreeNode {self.op}\n"
        for node in self.children:
            s += f"{node.tostring(tabdepth + 1)}\n"
        return s
    
    def get_comp_string(self):
        compstring = ""
        opstring = "+" if isinstance(self.op, ast.Add) else "*"
        for i in range(len(self.children)):
            leaf = self.children[i]
            compstring += f"({leaf.get_comp_string()})"
            if i < len(self.children) - 1:
                compstring += opstring

        return compstring

class ParseTreeLeaf:
    def __init__(self, comp):
        self.comp = str(comp)

    def tostring(self, tabdepth=0):
        return "\t"*tabdepth + self.comp
    
    def get_comp_string(self):
        return f"({self.comp})"
    
    def __str__(self):
        return self.tostring()
    
    def __eq__(self, other):
        if not isinstance(other, ParseTreeLeaf):
            return False
        
        return self.comp == other.comp
    
    def __lt__(self, other):
        if not isinstance(other, ParseTreeLeaf):
            return False

        return self.comp < other.comp

# Takes in computation string (e.g. "1 * 2 + 3") and returns our custom parse tree representation
def build_parse_tree(comp):
    parse_tree = ast.parse(comp.strip()).body[0].value
    return ParseTreeNode(parse_tree) if isinstance(parse_tree, ast.BinOp) else ParseTreeLeaf(parse_tree)

def get_common_children(tree1, tree2):
    common_children = []
    tree2_children: list = tree2.children[:]

    for child in tree1.children:
        for i in range(len(tree2_children)):
            other = tree2_children[i]
            if child == other:
                common_children.append(child)
                tree2_children.pop(i)
                break

    return common_children

'''
Find largest common computation between tree1 and tree2
    1. Compare roots of tree1 and tree2
        * If same op, then compare the children
            - If at least 2 children are shared, return new root with above op whose children are the shared 
            children
            - If only one child is shared, return a new tree whose root is that child
            - If no children are shared, the shared computation can't start at this node - repeat the process for each pair of children and record the largest shared computation
'''
def get_common_computation(tree1: ParseTreeNode, tree2: ParseTreeNode):
    if tree1.op == tree2.op:
        common_children = get_common_children(tree1, tree2)
        if len(common_children) >= 2:
            return [ParseTreeNode(tree1.op, get_common_children(tree1, tree2))]
        if len(common_children) == 1 and isinstance(common_children[0], ParseTreeNode):
            return [common_children[0]]
        
        common_comps = []
        for child1 in tree1.children:
            for child2 in tree2.children:
                if isinstance(child1, ParseTreeNode) and isinstance(child2, ParseTreeNode):
                    comp = get_common_computation(child1, child2)
                    if comp != None:
                        if isinstance(comp, list):
                            common_comps.extend(comp)
                        elif comp != None:
                            common_comps.append(comp)
        
        return common_comps if len(common_comps) > 0 else None
    
    common_comps = []
    for child in tree2.children:   # Guaranteed to be same op
        if isinstance(child, ParseTreeNode):
            comp = get_common_computation(tree1, child)
            if isinstance(comp, list):
                common_comps.extend(comp)
            elif comp != None:
                common_comps.append(comp)

    for child in tree1.children:   # Guaranteed to be same op
        if isinstance(child, ParseTreeNode):
            comp = get_common_computation(child, tree2)
            if isinstance(comp, list):
                common_comps.extend(comp)
            elif comp != None:
                common_comps.append(comp)

    return common_comps if len(common_comps) > 0 else None

# Get all the leaves in a parse tree
def get_leaves(tree: ParseTreeNode):
    leaves = []
    for child in tree.children:
        if isinstance(child, ParseTreeLeaf):
            leaves.append(child)
        else:
            leaves.extend(get_leaves(child))

    return leaves

# Do the children of comp form a proper "subset" of the children of tree? 
def is_comp_subset(tree: ParseTreeNode, comp: ParseTreeNode):
    if isinstance(tree, ParseTreeLeaf):
        return False

    if tree.op == comp.op:
        is_subset = all(item in tree.children for item in comp.children)
        if is_subset:
            return True
        
    is_subset_children = False
    for child in tree.children:
        is_subset_children = is_subset_children or is_comp_subset(child, comp)

    return is_subset_children

def size(tree):
    if isinstance(tree, ParseTreeLeaf):
        return 1
    
    s = 0
    for child in tree.children:
        s += size(child)

    return s

'''
Replacing computation with x:
1. Determine whether x is a subtree (or part of a subtree) of the main tree
2. If x makes up an entire subtree, replace that entire subtree with x
3. If x does not make up an entire subtree (but shares some children with one), replace only those children with x and leave the 
root intact
'''
def replace_comp(tree: ParseTreeNode, comp: ParseTreeNode, replace: ParseTreeLeaf):
    if isinstance(tree, ParseTreeLeaf) or isinstance(comp, ParseTreeLeaf):
        return tree

    if tree.op == comp.op:
        if all(item in tree.children for item in comp.children):
            if len(tree.children) > len(comp.children):
                # Subtract comp.children from tree.children
                comp_children = comp.children[:]
                for _ in range(len(comp_children)):
                    child = comp_children.pop()
                    for j in range(len(tree.children)):
                        if tree.children[j] == child:
                            tree.children.pop(j)
                            break

                tree.children.append(replace)
                return tree
            else:
                return replace
        else:
            for child in tree.children:
                if isinstance(child, ParseTreeNode):
                    child = replace_comp(child, comp, replace)

            return tree

    else:
        for child in tree.children:
            if isinstance(child, ParseTreeNode):
                child = replace_comp(child, comp, replace)

        return tree

# Read from our file - actual computations start here now
def reassign_shared_computations(file_in, file_out):
    NUM_VARS = how_big_is_it(file_in)
    print(f"{NUM_VARS} vars")

    regex = "t\\[[0-9]+\\] =[^;]*;"
    regex = re.compile(regex)

    file = open(file_in, "r+")
    contents = file.read()

    usages = [set() for _ in range(NUM_VARS)]
    parse_trees = [None for _ in range(NUM_VARS)]
    comp_list = re.findall(regex, contents)

    replaceable_vars = []   # How many variables are replaceable in each shared comp tree?
    comp_trees_freq = []        # Shared computations

    # Assume both parse trees are shared computations
    def compare_replaceable(parse_tree1, parse_tree2):
        repl1 = replaceable_vars[comp_trees_freq.index(parse_tree1)]
        repl2 = replaceable_vars[comp_trees_freq.index(parse_tree2)]
        return repl2 - repl1 if repl1 != repl2 else size(parse_tree1) - size(parse_tree2)

    '''
    For all t[i] in t:
        - Record all line #s where t[i] gets used (e.g. t[1]: [5, 10, 12, 17, ...]) - done!
        - If t[i] is in a shared computation C, determine the last usage of t[i] that is NOT in this computation - done!
            - If the last usage is before any shared computations, t[i] can be reclaimed; this needs to be the case for at least two variables in this computation to replace - done!
    '''
    for i in range(len(comp_list)):
        comp = comp_list[i]
        eqsign = comp.find("=")
        lhs = comp[:eqsign - 1]
        rhs = comp[eqsign + 2:-1]
        rhs = re.sub("\\s*", "", rhs)

        t_var = int(lhs[2:-1])
        parse_rhs = build_parse_tree(rhs)
        rhs_leaves = []
        if isinstance(parse_rhs, ParseTreeNode):
            rhs_leaves = [i.comp for i in get_leaves(parse_rhs)]
        else:
            rhs_leaves = [parse_rhs.comp]

        for leaf in rhs_leaves:
            rhs_var = -1
            if leaf[0] == "t":
                rhs_var = int(leaf[2:-1])
                usages[rhs_var].add(i)

        parse_trees[i] = parse_rhs

    usages = [sorted(i) for i in usages]

    comp_trees_linenos = []
    comp_trees_by_line = [[] for _ in range(NUM_VARS)]      # What shared computations are at each variable #?

    for i in range(NUM_VARS):
        for j in range(i + 1, NUM_VARS):
            if isinstance(parse_trees[i], ParseTreeNode) and isinstance(parse_trees[j], ParseTreeNode):
                common_comp = get_common_computation(parse_trees[i], parse_trees[j])
                if common_comp != None:
                    for comp in common_comp:
                        try:
                            comp_idx = comp_trees_freq.index(comp)
                            lineno_set = comp_trees_linenos[comp_idx]
                            lineno_set.add(i)
                            lineno_set.add(j)
                        except ValueError:
                            comp_trees_freq.append(comp)
                            lineno_set = set()
                            lineno_set.add(i)
                            lineno_set.add(j)
                            comp_trees_linenos.append(lineno_set)

    comp_trees_linenos = [sorted(list(lineno_set)) for lineno_set in comp_trees_linenos]

    all_linenos = set()     # Shared computations occur on which lines?
    for lineno_set in comp_trees_linenos:
        for l in lineno_set:
            all_linenos.add(l)

    for i in range(NUM_VARS):
        parse_tree = parse_trees[i]
        if parse_tree == None:
            continue
        for j in range(len(comp_trees_freq)):
            shared_comp_tree = comp_trees_freq[j]

            if isinstance(parse_tree, ParseTreeNode) and is_comp_subset(parse_tree, shared_comp_tree):
                comp_trees_by_line[i].append(shared_comp_tree)

    last_nonshared_usages = [-1 for _ in range(NUM_VARS)]
    for i in range(NUM_VARS):
        for u in usages[i]:
            if u not in all_linenos:
                last_nonshared_usages[i] = u

    for i in range(len(comp_trees_freq)):
        comp = comp_trees_freq[i]
        comp_vars = [i.comp for i in get_leaves(comp)]
        replaceable = 0

        for var in comp_vars:
            if var[0] == "t":
                t_var = int(var[2:-1])
                if last_nonshared_usages[t_var] < comp_trees_linenos[i][0]:
                    replaceable += 1

        replaceable_vars.append(replaceable)
    '''
    Final replacement alg:
    - Scan each line of the file
    - If the line contains an RHS computation, convert it into a parse tree (and increment our parse tree idx by 1)
        - Check if the parse tree index corresponds to any shared computations
            - If it does, perform the replacement with any shared computation with >= 2 of replaceable variables (in order of replaceable vars)
            - If this is the first time we're replacing this computation, output a line before it like 't[22239] = [shared computation]'
    '''
    file = open(file_in, "r+")

    new_file = open(file_out, "w")
    line = file.readline()
    tree_idx = 0

    for idx, shared_comp in comp_trees_freq:
        new_file.write(f"// REPEATED COMPUTATION\n")
        new_file.write(f"t[{idx + NUM_VARS}] = {shared_comp.get_comp_string()};\n")

    while line:
        comp = re.findall(regex, line)
        if len(comp) == 0:
            new_file.write(line)
            line = file.readline()
            continue

        comp = comp[0]
        eqsign = comp.find("=")
        lhs = comp[:eqsign - 1]
        rhs = comp[eqsign + 2:-1]

        if len(comp_trees_by_line[tree_idx]) == 0:
            tree_idx += 1
            new_file.write(line)
            line = file.readline()
            continue

        shared_comps = comp_trees_by_line[tree_idx]
        comps_to_replace = []
        for c in shared_comps:
            if replaceable_vars[comp_trees_freq.index(c)] >= 2:
                comps_to_replace.append(c)

        sorted(comps_to_replace, key=cmp_to_key(compare_replaceable))
        parse_rhs = build_parse_tree(rhs)
        for replace in comps_to_replace:
            best_idx = comp_trees_freq.index(replace)
            parse_rhs = replace_comp(parse_rhs, replace, ParseTreeLeaf(f"t[{best_idx + NUM_VARS}]"))
        
        new_comp_str_rhs = parse_rhs.get_comp_string()
        new_comp = f"{lhs} = {new_comp_str_rhs};\n"
        new_file.write(new_comp)

        tree_idx += 1
        line = file.readline()

if __name__ == "__main__":
    out_dir = "./out_files/3b"
    reassign_shared_computations(f"{out_dir}/noskips.cpp", f"{out_dir}/barn.cpp")
