import re

from howBIGisit import how_big_is_it

def remove_df(file_in, file_out):
    num_df = 4138
    num_t_vars = how_big_is_it(file_in)
    df_expr = ["" for _ in range(num_df)]
    df_to_t_lookup = ["" for _ in range(num_df)]
    t_to_t = ["" for _ in range(num_t_vars)]
    
    df_regex = re.compile("df\[[0-9]+\] = [^;]*;")
    t_regex = re.compile("t\[[0-9]+\] = df\[[0-9]+\];")
    df_df_regex = re.compile("df\[[0-9]+\] = df\[[0-9]+\];")
    df_var_regex = re.compile("df\[[0-9]+\]")
    t_var_regex = re.compile("t\[[0-9]+\]")

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

        new_index = num_t_vars + index
        df_to_t_lookup[old_index] = f"t[{new_index}]"
        return f"t[{new_index}]"

    # convert df[a] into t[b]
    def fix_df(match):
        match_str = match.group(0)
        return df_to_t(match_str)
    
    # convert t[a] into t[c] if t[a] = df[b] and df[b] => t[c]
    def fix_t_df(match):
        match_str = match.group(0)[2:-1]
        index = int(match_str)

        if index < num_t_vars:
            new_t = t_to_t[index]
            if new_t != "":
                return t_to_t[index]
            
        return f"t[{index}]"

    file = open(file_in, "r+")
    new_file = open(file_out, "w")
    line = file.readline()

    while line:
        rhs = re.findall(t_regex, line)
        if len(rhs) > 0:
            rhs = rhs[0]
            eqsign = rhs.find("=")
            lhs = rhs[:eqsign - 1]
            lhs_idx = int(lhs[3:-1])
            rhs = rhs[eqsign + 2:-1]
            t_to_t[lhs_idx] = df_to_t(rhs)
            line = file.readline()
            continue

        if re.search(df_df_regex, line) is not None:
            line = file.readline()
            continue

        line = re.sub(df_var_regex, fix_df, line)
        line = re.sub(t_var_regex, fix_t_df, line)
        new_file.write(line)
        line = file.readline()
