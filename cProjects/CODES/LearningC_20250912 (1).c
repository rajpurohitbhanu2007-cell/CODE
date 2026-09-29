// I'm including the standard input/output library for things like printf and scanf.
#include <stdio.h>
// I'll need this for some math functions, like ceil().
#include <math.h>

// I'm declaring a few global variables here, just to show how they work.
// They're accessible from any function in this file.
int global_int;
float global_float;
double global_double;
char global_char;

// I like to declare all my functions at the top, so the compiler knows they exist.
// These are called function prototypes.
void find_greatest_number();
void find_age_in_future();
void find_cumulative_sum();
void loop_with_break();
void loop_with_continue();
void check_array_length();
void loop_and_break_on_condition();
void loop_and_break_on_array_value();
void perform_simple_addition();
void calculate_profit_or_loss();
void calculate_percentage();
void generate_multiplication_table();
void loop_through_array_and_print();
void demonstrate_global_variables();
int negate_element(int k);
int sum_array(int arr[], int n);
int sum_2d_array(int arr[][2]);

// This is my main function, where everything kicks off.
int main() {
    // Just a little welcome message for myself or anyone running this.
    printf("Welcome to the Combined C Program!\n\n");
    
    // I'm calling each of my functions one by one to test them out.
    printf("--- 1. GREATEST OF THREE NUMBERS ---\n");
    find_greatest_number();
    printf("\n");

    printf("--- 2. AGE IN THE FUTURE ---\n");
    find_age_in_future();
    printf("\n");

    printf("--- 3. CUMULATIVE SUM (1-10) ---\n");
    find_cumulative_sum();
    printf("\n");

    printf("--- 4. LOOP WITH BREAK (USER INPUT) ---\n");
    loop_with_break();
    printf("\n");
    
    printf("--- 5. LOOP WITH CONTINUE (USER INPUT) ---\n");
    loop_with_continue();
    printf("\n");

    printf("--- 6. ARRAY LENGTH CALCULATION ---\n");
    check_array_length();
    printf("\n");

    printf("--- 7. LOOP WITH BREAK (ON CAPACITY THRESHOLD) ---\n");
    loop_and_break_on_condition();
    printf("\n");

    printf("--- 8. LOOP THROUGH ARRAY WITH BREAK ---\n");
    loop_and_break_on_array_value();
    printf("\n");
    
    printf("--- 9. SIMPLE ADDITION ---\n");
    perform_simple_addition();
    printf("\n");

    printf("--- 10. PROFIT OR LOSS CALCULATION ---\n");
    calculate_profit_or_loss();
    printf("\n");

    printf("--- 11. PERCENTAGE CALCULATION ---\n");
    calculate_percentage();
    printf("\n");
    
    printf("--- 12. MULTIPLICATION TABLE GENERATOR ---\n");
    generate_multiplication_table();
    printf("\n");
    
    printf("--- 13. LOOP THROUGH ARRAY AND PRINT ---\n");
    loop_through_array_and_print();
    printf("\n");
    
    printf("--- 14. GLOBAL VARIABLES ---\n");
    demonstrate_global_variables();
    printf("\n");
    
    printf("--- 15. PASSING ARRAY ELEMENTS TO A FUNCTION ---\n");
    {
        // Here, I'm just passing individual elements of my array to a function.
        int arr[] = { 10, 20, 30 };
        printf("Original array: {10, 20, 30}\n");
        // I'm changing the first two elements to their negative values.
        arr[0] = negate_element(arr[0]);
        arr[1] = negate_element(arr[1]);
        // Let's print the array to see the changes.
        for (int i = 0; i < 3; i++) {
            printf("%d\t", arr[i]);
        }
        printf("\nOutput should be: -10\t-20\t30\n");
    }
    printf("\n");

    printf("--- 16. PASSING ENTIRE 1D ARRAY TO A FUNCTION ---\n");
    {
        // Now I'm passing the whole array to my sum_array function.
        int arr[] = { 10, 20, 30 };
        // I have to calculate the length and pass it too.
        int n = sizeof(arr) / sizeof(arr[0]);
        printf("Sum of all elements in arr: %d\n", sum_array(arr, n));
    }
    printf("\n");

    printf("--- 17. PASSING ENTIRE 2D ARRAY TO A FUNCTION ---\n");
    {
        // Same idea, but this time with a 2D array.
        int arr[][2] = { {10, 20}, {30, 40} };
        printf("Sum of all elements in arr: %d\n", sum_2d_array(arr));
    }
    printf("\n");
    
    printf("All programs have finished executing.\n");
    
    // Returning 0 tells the system that my program ran successfully.
    return 0;
}

// This function finds the biggest of three numbers I enter.
void find_greatest_number() {
    int x, y, z;
   
    // Asking for the numbers.
    printf("Input three whole numbers: ");
    scanf("%d %d %d", &x, &y, &z);
    
    // A simple if-else ladder to compare them.
    if (x > y && x > z) {
        printf("%d is the greatest.\n", x);
    } else if (y > x && y > z) {
        printf("%d is the greatest.\n", y);
    } else if (z > y && z > x) {
        printf("%d is the greatest.\n", z);
    } else {
        // This is my catch-all for when numbers are equal.
        printf("Two or more numbers are equal or all of them are equal.\n");
    }
}

// A fun little function to figure out my age in the future.
void find_age_in_future() {
    int current_age, current_year, future_year;
    
    // Getting the info I need.
    printf("Please write your current age in years: ");
    scanf("%d", &current_age);
    
    printf("Please write the year you are at now: ");
    scanf("%d", &current_year);
    
    printf("Please write the year you want to find your age in: ");
    scanf("%d", &future_year);
    
    // Here's the calculation. It's the difference in years plus my current age.
    int future_age = future_year - current_year + current_age;
    
    printf("In %d, you will be %d years old.\n", future_year, future_age);
}

// I'm using a while loop to add up all the numbers from 1 to 10.
void find_cumulative_sum() {
    int sum = 0, i = 1;
    
    while (i <= 10) {
        sum = sum + i; // or I could write sum += i;
        i++;
    }
    
    printf("Cumulative Sum of numbers between 1-10: %d\n", sum);
}

// Testing out the 'break' statement.
void loop_with_break() {
    int num;
    // I'm giving the user 5 chances.
    for(int i = 5; i > 0; i--) {
        printf("Chances left - %d\n", i);
        printf("Enter a number between 0-99: ");
        scanf("%d", &num);
        
        // If the input is bad, I'm just ending the loop immediately.
        if (num > 99 || num < 0) {
            printf("Wrong Input! The number entered was %d\n", num);
            break; // Stop everything and get out of the loop.
        }
        
        printf("Input accepted as %d\n", num);
    }
    printf("Loop terminated.\n");
}

// This is similar, but I'm using 'continue' instead of 'break'.
void loop_with_continue() {
    int num;
    for (int i = 5; i > 0; i--) {
        printf("Chances left - %d\n", i);
        printf("Enter a number between 0-99: ");
        scanf("%d", &num);
        
        // If the input is bad...
        if (num > 99 || num < 0) {
            printf("Wrong Input! Skipping this round.\n");
            continue; // ...I'll just skip to the next iteration of the loop.
        }
        
        // This line only runs if the input was good.
        printf("Input Accepted as %d\n", num);
    }
    printf("Loop finished.\n");
}

// Here, I'm showing how to find the length of an array. It's a neat trick.
void check_array_length() {
    double temperature[] = { 39.0, 38.6, 36.2, 36.6, 37.0, 37.4, 38.2 };
    // I get the total size of the array in bytes and divide it by the size of one element.
    int length = sizeof(temperature) / sizeof(temperature[0]);
    
    printf("The length of the temperature array is: %d\n", length);
}

// Another example of using 'break'.
void loop_and_break_on_condition() {
    int n, threshold;
    printf("Enter a capacity (e.g., 100): ");
    scanf("%d", &n);
    
    // I'm setting a threshold at 50% of the capacity.
    threshold = (int)(n * 0.50); 
    
    printf("Actual Capacity: %d\n", n);
    printf("Threshold at: %d\n\n", threshold);
    
    // I'll loop and add 10 each time.
    for (int i = 0; i <= n; i = i + 10) {
        // Once I go over the threshold, I'll stop.
        if (i > threshold) {
            printf("50%% capacity reached! Stopping.\n");
            break;
        }
        printf("Passengers Onboarded: %d\n", i);
    }
    printf("Onboarding process finished.\n");
}

// Here I'm looping through an array and breaking when I find a specific value.
void loop_and_break_on_array_value() {
    float temperatures[] = { 39.0, 38.6, 36.2, 36.6, 37.0, 37.4, 38.2 };
    int length = sizeof(temperatures) / sizeof(temperatures[0]);
    
    printf("Current temperatures:\n");
    for (int i = 0; i < length; i++) {
        // I'm using ceil() to round up. If it rounds to 37, I'll stop.
        if (ceil(temperatures[i]) == 37) {
            printf("The temperature is %.1f, which rounds up to 37. Loop will now stop.\n", temperatures[i]);
            break;
        } else {
            // Otherwise, I just print the temperature.
            printf("%.1f\n", temperatures[i]);
        }
    }
}

// A super basic function to add two numbers. Can't go wrong with this!
void perform_simple_addition() {
    int num1, num2, result;
    
    printf("Enter the first number: ");
    scanf("%d", &num1);
    
    printf("Enter the second number: ");
    scanf("%d", &num2);
    
    result = num1 + num2;
    printf("The sum of %d and %d is: %d\n", num1, num2, result);
}

// Time to see if I made any money.
void calculate_profit_or_loss() {
    float cost_price, selling_price;
    
    printf("Enter the cost price: ");
    scanf("%f", &cost_price);
    
    printf("Enter the selling price: ");
    scanf("%f", &selling_price);
    
    if (selling_price > cost_price) {
        printf("You have a profit of %.2f\n", selling_price - cost_price);
    } else if (cost_price > selling_price) {
        printf("You have a loss of %.2f\n", cost_price - selling_price);
    } else {
        printf("You have neither a profit nor a loss.\n");
    }
}

// A simple percentage calculator. Useful for exams!
void calculate_percentage() {
    float total_marks, obtained_marks, percentage;
    
    printf("Enter the total marks: ");
    scanf("%f", &total_marks);
    
    printf("Enter the marks obtained: ");
    scanf("%f", &obtained_marks);
    
    // The classic percentage formula.
    percentage = (obtained_marks / total_marks) * 100;
    
    printf("Your percentage is: %.2f%%\n", percentage);
}

// I wrote this to generate a multiplication table for any number.
void generate_multiplication_table() {
    int num, i;
    
    printf("Enter a number to generate its table: ");
    scanf("%d", &num);
    
    // A for loop from 1 to 10 is perfect for this.
    for (i = 1; i <= 10; i++) {
        printf("%d * %d = %d\n", num, i, num * i);
    }
}

// Just a simple example of looping through an array and printing its contents.
void loop_through_array_and_print() {
    int a[] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
    int i;
    
    for (i = 0; i < 10; i++) {
        printf("The number is: %d\n", a[i]);
    }
}

// This function shows what values my global variables have by default (which is zero).
void demonstrate_global_variables() {
    printf("Default global_int: %d\n", global_int);
    printf("Default global_float: %f\n", global_float);
    printf("Default global_double: %lf\n", global_double);
    printf("Default global_char: %c\n", global_char);
    printf("Note: The char variable may appear blank because its default value is the null character '\\0'.\n");
}

// A handy function to just multiply a number by -1.
int negate_element(int k) {
    return k * -1;
}

// This function takes an array and its size, then adds up all the numbers.
int sum_array(int arr[], int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum = sum + arr[i];
    }
    return sum;
}

// Similar to the last one, but for a 2x2 array. I need nested loops for this.
int sum_2d_array(int arr[][2]) {
    int sum = 0;
    // The outer loop handles the rows.
    for (int i = 0; i < 2; i++) {
        // The inner loop handles the columns.
        for (int j = 0; j < 2; j++) {
            sum = sum + arr[i][j];
        }
    }
    return sum;
}
