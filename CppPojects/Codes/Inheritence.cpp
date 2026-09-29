#include<iostream>
using namespace std;

class A{
    protected:
    int x;
    public:
    void input(){
        cout<<"Enter the number : ";
        cin>>x;
    }
};
class B : public A{
    public:
    int y;
    void getData(){
        cout<<"Enter the number : ";
        cin>>y;
    }
    void add(){
        cout<<"Addition = "<<x+y;
    }
};
int main(){
    B a;
    a.input();
    a.getData();
    a.add();
    return 0;
}