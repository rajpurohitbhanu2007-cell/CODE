#include <iostream>
#include <string>
using namespace std;

class Student {
public:
    string name;
    int age;
    
    Student(string n, int a) {
        name = n;
        age = a;
    }
    Student(const Student &c){
        name = c.name;
        age = c.age;
    }
    void display(){
        cout << "Name: " << name << endl;
        cout << "Age: " << age <<endl;
    }
};

int main() {
    Student s1("Yoyo",30);
    Student s2 = s1;
    s2.display();
    return 0;
}