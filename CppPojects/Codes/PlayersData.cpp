#include<iostream>
#include<cstring>
using namespace std;
//Declaring functions
void display();
void insert();
void change();
//===================================

//Main function start
int main(){
int age;
char name[50],team[50];

    return 0:
}

//==================================
//Function Defination

//function to display all the data
void display(){
    cout<<"Team Name : "<<team;
    cout<<"Player Name : "<<name;
    cout<<"PLayer Age : "<<age;    
}
//function to get the values
void input(){
    cout<<"Enter Team Name : ";
    cin>>team;
    cout<<"Enter PLayer Name : ";
    cin>>name;
    cout<<"Enter Player Age : ";
    cin>>age;
}

//function for changing the values
void change(char newName[40],char newTeam[40],int newAge){ 
    strcpy(name,newName);
    strcpy(team,newTeam);
    age = newAge;
}
    