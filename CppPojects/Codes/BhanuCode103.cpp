#include <iostream>
#include <string>
using namespace std;
class calculate{
    
    public:
    void add(double a,double b){
       double c;
       c = a + b;
       cout<<"Double: "<<c<<endl;
    }
    void add(int a,int b){
       int c;    
       c = a + b;
       cout<<"Int: "<<c<<endl;
    }
    void add(int a,double b){
       double c;    
       c = a + b;
       cout<<"double: "<<c<<endl;
    }
};
int main(){
    calculate c1;
    c1.add(2,4);
    c1.add(2,4.6);
    c1.add(2.4,4.6);
    return 0;
}
