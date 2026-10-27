#include <iostream>
#include <string>
using namespace std;

class Student {
private:
    int roll;
    string name;
    float marks;
    static int count;

public:
    Student() {
        roll = 0;
        name = "";
        marks = 0;
        count++;
    }

    void input() {
        cout << "Enter Roll No: ";
        cin >> roll;

        cout << "Enter Name: ";
        cin >> name;

        cout << "Enter Marks: ";
        cin >> marks;

        if (marks < 0 || marks > 100) {
            cout << "Invalid marks! Enter 0 to 100.\n";
            marks = 0;
        }
    }

    void setMarks(float marks) {
        if (marks >= 0 && marks <= 100)
            this->marks = marks;
        else
            cout << "Invalid marks!\n";
    }

    int getRoll() {
        return roll;
    }

    float getMarks() {
        return marks;
    }

    static void showCount() {
        cout << "Total student objects: " << count << endl;
    }

    friend void showStudent(Student s);

    virtual void display() {
        cout << "Roll No: " << roll << endl;
        cout << "Name: " << name << endl;
        cout << "Marks: " << marks << endl;
    }

    virtual ~Student() {
        count--;
    }
};

int Student::count = 0;

void showStudent(Student s) {
    cout << "Name: " << s.name << endl;
    cout << "Marks: " << s.marks << endl;
}

class Result : public Student {
public:
    void display() override {
        Student::display();

        if (getMarks() >= 40)
            cout << "Result: Pass\n";
        else
            cout << "Result: Fail\n";
    }
};

int main() {
    const int MAX = 100;
    Student* students[MAX];
    int count = 0;
    int choice;

    do {
        cout << "\n===== STUDENT MANAGEMENT SYSTEM =====\n";
        cout << "1. Add Student\n";
        cout << "2. Display Students\n";
        cout << "3. Search Student\n";
        cout << "4. Update Marks\n";
        cout << "5. Delete Student\n";
        cout << "6. Show Total Objects\n";
        cout << "0. Exit\n";
        cout << "Enter choice: ";
        cin >> choice;

        switch (choice) {
            case 1: {
                if (count == MAX) {
                    cout << "Student list is full!\n";
                    break;
                }

                Student* s = new Result();
                s->input();

                bool duplicate = false;

                for (int i = 0; i < count; i++) {
                    if (students[i]->getRoll() == s->getRoll()) {
                        duplicate = true;
                        break;
                    }
                }

                if (duplicate) {
                    cout << "Roll number already exists!\n";
                    delete s;
                } else {
                    students[count] = s;
                    count++;
                    cout << "Student added successfully!\n";
                }
                break;
            }

            case 2:
                if (count == 0) {
                    cout << "No student records found!\n";
                }

                for (int i = 0; i < count; i++) {
                    cout << "\nStudent " << i + 1 << endl;
                    students[i]->display();
                }
                break;

            case 3: {
                int roll, found = -1;
                cout << "Enter Roll No to search: ";
                cin >> roll;

                for (int i = 0; i < count; i++) {
                    if (students[i]->getRoll() == roll) {
                        found = i;
                        break;
                    }
                }

                if (found == -1)
                    cout << "Student not found!\n";
                else
                    students[found]->display();

                break;
            }

            case 4: {
                int roll, found = -1;
                float marks;

                cout << "Enter Roll No: ";
                cin >> roll;

                for (int i = 0; i < count; i++) {
                    if (students[i]->getRoll() == roll) {
                        found = i;
                        break;
                    }
                }

                if (found == -1) {
                    cout << "Student not found!\n";
                } else {
                    cout << "Enter new marks: ";
                    cin >> marks;
                    students[found]->setMarks(marks);
                }
                break;
            }

            case 5: {
                int roll, found = -1;
                cout << "Enter Roll No to delete: ";
                cin >> roll;

                for (int i = 0; i < count; i++) {
                    if (students[i]->getRoll() == roll) {
                        found = i;
                        break;
                    }
                }

                if (found == -1) {
                    cout << "Student not found!\n";
                } else {
                    delete students[found];

                    for (int i = found; i < count - 1; i++) {
                        students[i] = students[i + 1];
                    }

                    count--;
                    cout << "Student object deleted successfully!\n";
                }
                break;
            }

            case 6:
                Student::showCount();
                break;

            case 0:
                cout << "Exiting program...\n";
                break;

            default:
                cout << "Invalid choice!\n";
        }

    } while (choice != 0);

    for (int i = 0; i < count; i++) {
        delete students[i];
    }

    return 0;
}
