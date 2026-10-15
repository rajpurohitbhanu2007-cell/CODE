#include<iostream>
using namespace std;
class Student{
private:
    string name;
    int age;
public:
    //1. Default Constructor
    Student(){
        name = "Unknown";
        age = 0;
        cout << "Default contructor called" << endl;
    }
    //2. Parameterized Constructor
    Student(string n, int a){
        name = n;
        age = a;
        cout << "Parameterized constructor called" << endl;
    }
    //3. Copy Constructor
    Student(const Student &s){
        name = s.name;
        age = s.age;
        cout << "Copy constructor called" << endl;
    } 
    //Display student details
    void display(){
        cout << "Name :" << name << endl;
        cout << "Age :" << age << endl;
    }
    ~Student(){
        cout << "Destructor called for" << name << endl;
    }
};
int main(){
    //Default constructor
    Student s1;
    s1.display();
    cout << "\n";
    //Parameterized constructor
    Student s2("Rahul", 20);
    s2.display();
    cout << "\n";
    //Copy constructor
    Student s3(s2);
    s3.display();
    return 0;
}

