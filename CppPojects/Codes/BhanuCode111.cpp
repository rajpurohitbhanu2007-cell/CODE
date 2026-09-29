#include<iostream>
using namespace std;

int main(){
    int n;
    cout<<"Enter number of elements : ";
    cin>>n;

    int *arr= new int[n];
    for(int i=0; i<n; i++){
        if(arr[i]%2==0){
            cout<<arr[i]<<"";
        }
    }delete [] arr;
    return 0; 
}
