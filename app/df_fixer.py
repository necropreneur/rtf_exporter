import pandas as pd

def fix_dataframe(df, columns_to_fix):
    # Define a function to fix individual cells
    def fix_cell(cell):
        # If the cell is not a string, return it as is
        if not isinstance(cell, str):
            return cell
        
        # Remove multiple spaces
        words = cell.split()
        
        fixed_words = []
        
        # Buffer to hold single letters
        single_letter_buffer = []
        
        for word in words:
            if len(word) == 1:
                # If word is a single letter, add it to the buffer
                single_letter_buffer.append(word)
            else:
                # If word is longer than one letter and buffer is not empty,
                # join the single letters and append
                if single_letter_buffer:
                    fixed_words.append("".join(single_letter_buffer))
                    single_letter_buffer = []
                
                fixed_words.append(word)
        
        # Check if there are any remaining single letters
        if single_letter_buffer:
            fixed_words.append("".join(single_letter_buffer))
        
        # Now fix two long words separated by multiple spaces
        final_words = []
        for word in fixed_words:
            if len(word) > 1:
                final_words.append(word)
        
        # If there are two long words, combine them with a single space
        if len(final_words) == 2:
            return " ".join(final_words)
        else:
            return " ".join(fixed_words)
        
    # Apply the fix_cell function to specified columns in the DataFrame
    for col in columns_to_fix:
        df[col] = df[col].apply(fix_cell)
    
    return df

if __name__ == "__main__":
    # Sample DataFrame
    data = {
        'col1': ['a b', 'hello     world', 3.14],
        'col2': ['d e f', 'python   pandas', 'g h i'],
        'col3': [1, 'k', 'l m'],
        'col4': [2.71, 'math', 'e f']
    }

    df = pd.DataFrame(data)

    print("Original DataFrame:")
    print(df)

    columns_to_fix = ['col1', 'col2', 'col4']
    fixed_df = fix_dataframe(df, columns_to_fix)
    print("Fixed DataFrame:")
    print(fixed_df)
