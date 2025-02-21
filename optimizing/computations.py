import re
import ast
import astor
from functools import cmp_to_key

from howBIGisit import how_big_is_it

# Custom parse tree data structure
class ParseTreeNode:
    def __init__(self, op, children):
        self.op = op
        self.children = children

    def tostring(self, tabdepth=0):
        s = "\t"*tabdepth + f"ParseTreeNode {self.op}\n"
        for node in self.children:
            s += f"{node.tostring(tabdepth + 1)}\n"
        return s
    
    def __str__(self):
        return self.tostring()
    
    def __eq__(self, other):
        if not isinstance(other, ParseTreeNode):
            return False
        
        if self.op == other.op and len(self.children) == len(other.children):
            for i in range(len(self.children)):
                if self.children[i] != other.children[i]:
                    return False
                
            return True
        
        return False
    
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

# Comparator function for comparing two parse tree nodes (note: we assume the parse tree node's children are already sorted)
def compare_trees(tree1, tree2):
    if isinstance(tree1, ParseTreeLeaf) and isinstance(tree2, ParseTreeLeaf):
        return 0 if tree1.comp == tree2.comp else (1 if tree1.comp > tree2.comp else -1)
    elif isinstance(tree1, ParseTreeLeaf) and isinstance(tree2, ParseTreeNode):
        return 1
    elif isinstance(tree1, ParseTreeNode) and isinstance(tree2, ParseTreeLeaf):
        return -1
    else:
        if len(tree1.children) != len(tree2.children):
            return len(tree2.children) - len(tree1.children)
        
        for i in range(len(tree1.children)):
            if compare_trees(tree1.children[i], tree2.children[i]) > 0:
                return 1
            elif compare_trees(tree1.children[i], tree2.children[i]) < 0:
                return -1
            
        return 0
    
'''
If node's children are all leaves then just sort them with sort()
Otherwise, go thru non-leaf children and call sort_tree on them
Then, sort all children with sort()
'''
def sort_tree(node: ParseTreeNode):
    all_leaves = True
    for child in node.children:
        if isinstance(child, ParseTreeNode):
            all_leaves = False
            break

    if all_leaves:
        node.children = sorted(node.children, key=cmp_to_key(compare_trees))
    else:
        for child in node.children:
            if isinstance(child, ParseTreeNode):
                sort_tree(child)
        
        node.children = sorted(node.children, key=cmp_to_key(compare_trees))

def condense_parse_tree(parse_tree: ParseTreeNode):
    same_op_node = None
    for node in parse_tree.children:
        if isinstance(node, ParseTreeNode) and node.op == parse_tree.op:
            same_op_node = node
            break

    while same_op_node:
        same_op_children = same_op_node.children
        parse_tree.children.remove(same_op_node)
        parse_tree.children += same_op_children

        same_op_node = None
        for node in parse_tree.children:
            if isinstance(node, ParseTreeNode) and node.op == parse_tree.op:
                same_op_node = node
                break

    for node in parse_tree.children:
        if isinstance(node, ParseTreeNode):
            condense_parse_tree(node)

def convert_parse_tree(parse_tree):
    if isinstance(parse_tree, ast.Subscript):
        # print(ast.dump(parse_tree, indent=4))
        arr = parse_tree.value.id
        idx = astor.to_source(parse_tree.slice).strip()[1:-1]
        # print(f"{arr}[{idx}]")
        return ParseTreeLeaf(f"{arr}[{idx}]")
    if isinstance(parse_tree, ast.Constant):
        return ParseTreeLeaf(parse_tree.value)
    else:
        node = ParseTreeNode(parse_tree.op, [])
        node_left = convert_parse_tree(parse_tree.left)
        node_right = convert_parse_tree(parse_tree.right)
        node.children.append(node_left)
        node.children.append(node_right)
        condense_parse_tree(node)
        sort_tree(node)
        return node

# Takes in computation string (e.g. "1 * 2 + 3") and returns our custom parse tree representation
def build_parse_tree(comp):
    parse_tree = ast.parse(comp.strip()).body[0].value
    return convert_parse_tree(parse_tree)

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

# DEBUG CODE
'''
parse_rhs = build_parse_tree("(t[22715] + t[22778]) * t[8618] + t[22829] * t[530] + t[22849] * t[422] + t[22873] * t[405] +                (t[1912] + t[20236] + t[22876] + t[22878] + (t[20271] + t[2191] * t[236]) * t[252] + t[22882] * t[278]) *                    t[278] +                (t[22899] + t[22905]) * t[647] +                (t[21796] + t[1916] + t[1918] + t[20618] + t[21798] + t[21800] +                 (t[4894] + t[20169] + t[8497] * t[85] + t[22909]) * t[164] +                 (t[2208] + t[20167] + t[20170] + t[22909] + t[2261] * t[236]) * t[236]) *                    t[236] +                (t[22947] + t[22976]) * t[3613] + (t[22982] + t[23002]) * t[1289] + (t[23083] + t[23140]) * t[4055] +                t[23155] * t[525] + (t[23167] + t[23178]) * t[566] + t[23213] * t[364] +                (t[1912] + t[20236] + t[22876] + t[22878] + t[22882] * t[252]) * t[252] +                (t[23324] + t[23374]) * t[11544] + (t[23414] + t[23436]) * t[3721] + t[23462] * t[383] +                t[23475] * t[333]")
print(parse_rhs)
best_comp2 = build_parse_tree("((t[1916]))+((t[20618]))")
best_comp1 = build_parse_tree("((t[1916]))+((t[1918]))+((t[20618]))+((t[21796]))+((t[21798]))+((t[21800]))")
parse_rhs = replace_comp(parse_rhs, best_comp1, ParseTreeLeaf("t[0]"))
parse_rhs = replace_comp(parse_rhs, best_comp2, ParseTreeLeaf("t[1]"))
print("=====")
print(parse_rhs)
print(parse_rhs.get_comp_string())
'''

# Read from our file - actual computations start here now
def reassign_shared_computations(file_in, file_out):
    NUM_VARS = how_big_is_it(file_in)

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

    comp_trees_by_line = [[] for _ in range(NUM_VARS)]      # What shared computations are at each variable #?

    for i in range(NUM_VARS):
        for j in range(i + 1, NUM_VARS):
            if isinstance(parse_trees[i], ParseTreeNode) and isinstance(parse_trees[j], ParseTreeNode):
                common_comp = get_common_computation(parse_trees[i], parse_trees[j])
                if common_comp != None:
                    for comp in common_comp:
                        try:
                            comp_trees_freq.index(comp)
                        except ValueError:
                            comp_trees_freq.append(comp)
    '''
    t[10] = t[1] + t[2] + t[3] + t[4] + t[5]
    t[11] = t[1] + t[2] + t[3] + t[4] + t[6]
    t[12] = t[1] + t[2] + t[3] + t[5] + t[6]
    t[13] = t[1] + t[2] + t[3] + t[5] + t[7]
    '''
    ''' for c in comp_trees_freq:
        print(c)

    print(len(comp_trees_freq)) '''

    comp_trees_linenos = [set() for _ in range(len(comp_trees_freq))]     # Shared computations get used at which lines?

    for i in range(NUM_VARS):
        parse_tree = parse_trees[i]
        if parse_tree == None:
            continue
        for j in range(len(comp_trees_freq)):
            shared_comp_tree = comp_trees_freq[j]
            # print(f"{i} {j}")
            # print(f"{parse_tree} {shared_comp_tree}")

            if isinstance(parse_tree, ParseTreeNode) and is_comp_subset(parse_tree, shared_comp_tree):
                idx = comp_trees_freq.index(shared_comp_tree)
                comp_trees_by_line[i].append(shared_comp_tree)
                comp_trees_linenos[idx].add(i)

    '''
    for i in range(len(comp_trees_by_line)):
        print(comp_list[i])
        for c in comp_trees_by_line[i]:
            print(c)
        
        print("====")
    '''

    ''' tree1 = parse_trees[27]
    tree2 = comp_trees_freq[0]

    print(tree1)
    print(tree2)
    print(is_comp_subset(tree1, tree2)) '''

    # print(comp_trees_linenos)

    usages_shared = [[] for _ in range(NUM_VARS)]   # Which shared computations are each variable used in?
    # print(len(comp_trees_freq))
    for i in range(len(comp_trees_freq)):
        comp = comp_trees_freq[i]
        comp_vars = [i.comp for i in get_leaves(comp)]
        for var in comp_vars:
            if var[0] == "t":
                t_var = int(var[2:-1])
                usages_shared[t_var].append(comp)

    # print(usages)

    for i in range(len(comp_trees_freq)):
        comp = comp_trees_freq[i]
        comp_vars = [i.comp for i in get_leaves(comp)]
        replaceable = 0
        linenos = sorted(comp_trees_linenos[i])

        # print(linenos)

        for var in comp_vars:
            if var[0] == "t":
                t_var = int(var[2:-1])

                # print(t_var)
                # print(f"{usages[t_var][-1]} {linenos}")
                if usages[t_var][-1] <= linenos[-1]:
                    # Variable isn't used after shared computation
                    last_usage = -1     # Last usage of t[i] that isn't in the shared computation
                    for j in usages[t_var]:
                        if j not in linenos:
                            last_usage = j
                            break

                    # print(last_usage)
                    if last_usage < linenos[0]:
                        # print(comp)
                        replaceable += 1
                        # print(replaceable)

        replaceable_vars.append(replaceable)

    # print(replaceable_vars)

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
    repl_idx = NUM_VARS     # t index to assign shared computation to

    repl_var = [-1 for _ in range(len(comp_trees_freq))]    # Which variable is each shared comp assigned to?

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
        # best_comp = shared_comps[0]
        for c in shared_comps:
            if replaceable_vars[comp_trees_freq.index(c)] >= 2:
                comps_to_replace.append(c)

        sorted(comps_to_replace, key=cmp_to_key(compare_replaceable))
        parse_rhs = build_parse_tree(rhs)
        for replace in comps_to_replace:
            best_idx = comp_trees_freq.index(replace)
            if repl_var[best_idx] < 0:
                ''' print(lhs)
                print(repl_var)
                for c in comps_to_replace:
                    print(c) '''

                new_file.write(f"// REPEATED COMPUTATION\n")
                new_file.write(f"t[{repl_idx}] = {replace.get_comp_string()};\n")
                repl_var[best_idx] = repl_idx
                repl_idx += 1

            parse_rhs = replace_comp(parse_rhs, replace, ParseTreeLeaf(f"t[{repl_var[best_idx]}]"))
        
        new_comp_str_rhs = parse_rhs.get_comp_string()
        new_comp = f"{lhs} = {new_comp_str_rhs};\n"
        new_file.write(new_comp)

        tree_idx += 1
        line = file.readline()
