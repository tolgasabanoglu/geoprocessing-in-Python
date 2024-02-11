# 1. Create a new variable called y and assign the value 42 to it. Check its data type and convert it into a string.
y = 42

# Check the data type 
data_type = type(y)
print(f"The data type of y is: {data_type}")

# Convert y into a string
y_str = str(y)

# Check the data type of y_str
data_type_str = type(y_str)
print(f"The data type of y_str is: {data_type_str}")

# 2. Create two string variables s1 and s2 holding "I study in" and "Berlin".
s1 = "I study in"
s2 = "Berlin"

# 2a. Write a loop that prints each letter of variable s2 ("Berlin")
for letter in s2:
    print(letter)

# 3. Concatenate the strings to read "I study in Berlin". Store the result in variable s3.
s3 = f"{s1} {s2}"

# 4. Replace the Word Berlin in variable 3 with Amsterdam. Calculate the number of characters the string has expanded.
s4 = s3.replace("Berlin", "Amsterdam") 
expansion = len(s4) - len(s3)
print(f"Expanded by {expansion} characters.")

# 5. Create a list called citylist of the following character strings: "Berlin", "Dresden", "Munich", "Berlin", "Munich".
citylist = ["Berlin", "Dresden", "Munich", "Berlin", "Munich"]

# 6. Loop through citylist and print the name of each city, as well as the number of characters the city name has.
for city in citylist:
    print(f"City: {city}, Number of Characters: {len(city)}")

# 7. How many characters has the longest city name in the list?
max_length = 0
longest_city = ""

for city in citylist:
    length = len(city)
    if length > max_length:
        max_length = length
        longest_city = city

print(f"The longest city name is '{longest_city}' with {max_length} characters.")

# 8. Add the city Rome to the citylist
citylist.append("Rome")

# 9. Berlin, Dresden, and Munich have a population of 3700000, 560000, and 1400000, respectively. 
# Create a dictionary that holds the city names as keys and the population as values.
city_population = {
    "Berlin": 3700000,
    "Dresden": 560000,
    "Munich": 1400000
}

# 10. Calculate the average population of the three cities based on the values stored in your previously created dictionary.
total_population = sum(city_population.values())
num_cities = len(city_population)
average_population = total_population / num_cities
print(f"The average population of the three cities is {average_population:.2f}")

# 11. Write a loop that prints the following sentence: "The population of CITY is POP.",
# replacing CITY and POP with the name of the city and the population.
for city, population in city_population.items():
    print(f"The population of {city} is {population}.")

# 12. Amend the loop by the following criterion: include the print-statements 
# "The city is larger than 1 Million" and "The city is smaller than 1 Million" 
# where the city population matches the criterion.
for city, population in city_population.items():
    if population > 1000000:
        print(f"The population of {city} is {population}. The city is larger than 1 Million.")
    else:
        print(f"The population of {city} is {population}. The city is smaller than 1 Million.")
