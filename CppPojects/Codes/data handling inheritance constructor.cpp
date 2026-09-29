#include <iostream>
using namespace std;

class Student {
private:
    int marks;
public:
    void setMarks(int m) {
        marks = m;
    }
    int getMarks() {
        return marks;
    }
};

class Person {
public:
    string name;
};

class StudentInherit : public Person {
public:
};

class StudentConst {
public:
    StudentConst() {
        cout << "Constructor";
    }
};

int main() {
    StudentConst s1;
    return 0;
}
