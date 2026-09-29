#include<stdio.h>
#include<math.h>
//Declaring functions.

int highest_marks(int row,int col,int arr[row][col]);
int lowest_marks(int row,int col,int arr[row][col]);
float average_marks(int row,int col,int arr[row][col]);
float Calculating_percentage(int row,int col,int arr[row][col]);
char Calculating_letter_grade(float percentage);

//=============================================================================================================

//global variables
int maxSub = 100;
//=============================================================================================================

//Main function starts here.
int main() {

    //Greetings.
    printf("Welcome To Student Grade Analyser");
    int stdNum,subNum;
    //Creating An Array.
    int grades[stdNum][subNum];
    
    //Taking inputs for stdNum and subNum.
    printf("\nEnter Student number to proceed :");
    scanf("%d",&stdNum);
    printf("\nEnter Subject number to proceed :");
    scanf("%d",&subNum);
    //printing the variables for check.
    printf("Total no. of Students : %d\nTotal no. of Subjects : %d\n",stdNum,subNum);

    //Loop for taking in grades.
    int length = sizeof(grades)/sizeof(grades[0][0]);
    for(int i=0; i<stdNum; i++) {
        for(int j=0; j<subNum; j++) {
            printf("Enter the Marks of Student %d for Subject %d : ",i+1,j+1);
            scanf("%d",&grades[i][j]);

        }
    }


    //Doing calculation and storing them in their respective variables
    int lowestMarks = lowest_marks(stdNum,subNum,grades);
    int highestMarks = highest_marks(stdNum,subNum,grades);
    float averageMarks = average_marks(stdNum,subNum,grades);

    //Calculating the percentage
    float percentage[stdNum];
    char letter_grade[stdNum];
    for(int i = 0; i<stdNum; i++) {
        percentage[i] = Calculating_percentage(stdNum,subNum,grades);
        //Calculating the Grades A,B,C,D,E & F.
        letter_grade[i] = Calculating_letter_grade(percentage[i]);
    }

    //main ends.
    return 0;
}

//=============================================================================================================
//Functions Definition

//function for finding highest marks
int highest_marks(int row,int col,int arr[row][col]) {
    int x = arr[0][0],y = arr[0][0];
    //loop to calculate highest
    for(int i=0; i<row; i++) {
        for(int j=0; j<col; j++) {
            if(x<arr[i][j]) {
                x = arr[i][j];
            }
        }
    }
    return x;
}

//Function for finding the lowest marks
int lowest_marks(int row,int col,int arr[row][col]) {
    int x = arr[0][0],y = arr[0][0];
    //loop to calculate lowest
    for(int i=0; i<row; i++) {
        for(int j=0; j<col; j++) {
            if(x>arr[i][j]) {
                x = arr[i][j];
            }
        }
    }
    return x;
}
//function for finding the average marks
float average_marks(int row,int col,int arr[row][col]) {
    int sum = 0;
    float x;
    //loop to calculate sum
    for(int i=0; i<row; i++) {
        for(int j=0; j<col; j++) {
            sum = sum + arr[i][j];
        }
    }
    //finding average
    x = (float)sum/(row*col);
    return x;
}
//finding percentage per student
float Calculating_percentage(int row,int col,int arr[row][col]) {
    int sum = 0;
    //loop for calculating sum
    for(int j = 0; j<col; j++) {
        sum = sum + arr[row][j];
    }
    //calculating percentage
    float x = (float)sum/(col*maxSub)*100;
    return x;
}
//finding grades for students by if else ladder
char Calculating_letter_grade(float percentage) {
    if(percentage>=91) {
        return 'A';
    }
    else if(percentage>=81) {
        return 'B';
    }
    else if(percentage>=71) {
        return 'C';
    }
    else if(percentage>=61) {
        return 'D';
    }
    else if(percentage>=51) {
        return 'E';
    }
    else {
        return 'F';
    }
}
//=============================================================================================================
    