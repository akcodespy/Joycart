# simple_utils.py - A tiny utility library

def reverse_string(text):
    """
    Return the input string with characters in reverse order.
    
    Parameters:
        text (str): The string to reverse.
    
    Returns:
        str: The reversed string.
    """
    return text[::-1]

def count_words(sentence):
    """
    Count the words in a sentence.
    
    Parameters:
        sentence (str): Input string whose words are counted.
    
    Returns:
        int: Number of whitespace-separated tokens in `sentence`.
    """
    return len(sentence.split())

def celsius_to_fahrenheit(celsius):
    """
    Convert a temperature from Celsius to Fahrenheit.
    
    Parameters:
        celsius (float | int): Temperature in degrees Celsius.
    
    Returns:
        float: Temperature converted to degrees Fahrenheit.
    """
    return (celsius * 9/5) + 32