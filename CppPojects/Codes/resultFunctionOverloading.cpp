#include<iostream>
using namespace std;

class Result{
    public:
    void marks(int marks){
        cout<<"Marks are : "<<marks<<endl;
    }
    void marks(float percentage){
        cout<<"percentage are : "<<percentage<<endl;
    }
    void marks(int m1, int m2, int m3){
        int total = m1+m2+m3;
        cout<<"Total Marks are : "<<total<<endl;
    }
};
int main(){
    Result r;
    r.marks(85);
    r.marks(85.5f);
    r.marks(85,90,95);
    return 0;
}