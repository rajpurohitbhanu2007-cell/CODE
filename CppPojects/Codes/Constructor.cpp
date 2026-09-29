#include <iostream>
using namespace std;

class Student {
public:
    int age;
    
    Student() {
        age = 20;
    }
};

int main() {
    Student s1;
    cout << "Age : " << s1.age << endl;
    return 0;
}
