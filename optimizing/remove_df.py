import re

from howBIGisit import how_big_is_it

# t[9301] = t[17570] * a[991] + t[17629] * t[2670] + t[9255] * a[979] + t[19324] * a[868] 
# + t[16771] * a[1142] + t[19193] * a[211] + t[19200] * a[72] + t[19234] * a[1034] + t[17159] 
# * t[1848] + t[17075] * a[807] + t[16094] * a[215] + t[16122] * a[483] + t[18022] * a[849] 
# + t[18759] * t[5179] + t[18811] * t[5253] + t[19867] * a[850] + t[19924] * t[7024] + t[18710] 
# * t[5030];

# t[9301] = df[1703] * a[991] + t[8282] * t[2670] + t[9255] * a[979] + df[3456] * a[868] 
# + t[8467] * a[1142] + t[7900] * a[211] + df[3330] * a[72] + t[7832] * a[1034] + t[8370] 
# * t[1848] + df[1206] * a[807] + df[230] * a[215] + df[252] * a[483] + t[8198] * a[849] 
# + t[7967] * t[5179] + t[7952] * t[5253] + df[3997] * a[850] + t[7661] * t[7024] + t[7976] 
# * t[5030];

def remove_df(file_in, file_out):
    num_df = 4138
    num_t_vars = how_big_is_it(file_in)
    df_expr = ["" for _ in range(num_df)]
    t_expr = ["" for _ in range(num_t_vars)]
    df_to_t_lookup = ["" for _ in range(num_df)]
    t_to_df_lookup = ["" for _ in range(num_t_vars)]
    t_to_t_lookup = ["" for _ in range(num_t_vars)]
    
    df_regex = re.compile("df\\[[0-9]+\\] = [^;]*;")
    t_regex = re.compile("t\\[[0-9]+\\] = [^;]*;")
    df_df_regex = re.compile("df\\[[0-9]+\\] = df\\[[0-9]+\\];")
    df_var_regex = re.compile("df\\[[0-9]+\\]")
    t_var_regex = re.compile("t\\[[0-9]+\\]")
    t_t_regex = re.compile("t\\[[0-9]+\\] = t\\[[0-9]+\\];")

    file = open(file_in, "r+")
    line = file.readline()

    while line:
        rhs = re.findall(df_regex, line)
        if len(rhs) > 0:
            rhs = rhs[0]
            eqsign = rhs.find("=")
            lhs = rhs[:eqsign - 1]
            lhs_idx = int(lhs[3:-1])
            rhs = rhs[eqsign + 2:-1]
            df_expr[lhs_idx] = rhs

        rhs = re.findall(t_regex, line)
        if len(rhs) > 0:
            rhs = rhs[0]
            eqsign = rhs.find("=")
            lhs = rhs[:eqsign - 1]
            lhs_idx = int(lhs[2:-1])
            rhs = rhs[eqsign + 2:-1]
            t_expr[lhs_idx] = rhs

        line = file.readline()

    # print(df_expr)

    def df_to_t(df):
        old_index = int(df[3:-1])
        if old_index >= num_df:
            return f"df[{old_index}]"
        
        index = old_index
        # print(index)
        if df_to_t_lookup[index] != "":
            return df_to_t_lookup[index]

        expr = df_expr[index]
        while re.fullmatch(df_var_regex, expr) is not None:
            index = int(expr[3:-1])
            expr = df_expr[index]

        if re.fullmatch(t_var_regex, expr):
            new_t = t_to_t(expr)
            new_df = t_to_df(new_t)
            if new_df == "":
                df_to_t_lookup[old_index] = new_t
                return new_t
            else:
                new_t = df_to_t(new_df)
                df_to_t_lookup[old_index] = new_t
                return new_t

        new_index = num_t_vars + index
        df_to_t_lookup[old_index] = f"t[{new_index}]"
        return f"t[{new_index}]"
    
    def t_to_df(t):
        old_index = int(t[2:-1])
        index = old_index
        # print(index)
        if index >= num_t_vars:
            return ""
        if t_to_df_lookup[index] != "":
            return t_to_df_lookup[index]

        expr = t_expr[index]
        while re.fullmatch(t_var_regex, expr) is not None:
            index = int(expr[2:-1])
            expr = t_expr[index]

        if re.fullmatch(df_var_regex, expr):
            t_to_df_lookup[old_index] = expr
            return expr
        
        return ""
    
    def t_to_t(t_var):
        index = int(t_var[2:-1])
        if index >= num_t_vars:
            return t_var
        if t_to_t_lookup[index] != "":
            return t_to_t_lookup[index]
        
        df = t_to_df(t_var)
        if df != "":
            new_t = df_to_t(df)
            t_to_t_lookup[index] = new_t
            return new_t
        
        old_expr = t_var
        expr = t_expr[index]
        while re.fullmatch(t_var_regex, expr) is not None:
            index = int(expr[2:-1])
            old_expr = expr
            expr = t_expr[index]
            
        return old_expr

    # convert df[a] into t[b]
    def fix_df(match):
        match_str = match.group(0)
        return df_to_t(match_str)
    
    # convert t[a] into t[c] if t[a] = df[b] and df[b] => t[c]
    def fix_t_df(match):
        match_str = match.group(0)
        return t_to_t(match_str)

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    while line:
        # Skip this line if it's df[??] = df[??];
        if re.search(df_df_regex, line) is not None:
            line = file.readline()
            continue

        line = re.sub(df_var_regex, fix_df, line)
        line = re.sub(t_var_regex, fix_t_df, line)
        if re.search(t_t_regex, line) is None:
            new_file.write(line)
            
        line = file.readline()

if __name__ == "__main__":
    remove_df("out_files/noaassignments.cpp", "out_files/nodf.cpp")
