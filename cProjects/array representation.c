#include <stdio.h>

#define MAX 20

int main() {
    int A[3][3] = {
        {1, 0, 0},
        {2, 0, 0},
        {0, 0, 3}
    };
    int B[3][3] = {
        {1, 1, 1},
        {2, 2, 2},
        {3, 3, 3}
    };

    int a[MAX][3], b[MAX][3], sum[MAX][3];

    // Convert Matrix A to sparse representation
    a[0][0] = 3; // Total rows
    a[0][1] = 3; // Total columns
    int k = 1;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (A[i][j] != 0) {
                a[k][0] = i;
                a[k][1] = j;
                a[k][2] = A[i][j];
                k++;
            }
        }
    }
    a[0][2] = k - 1; // Total non-zero elements in A

    // Convert Matrix B to sparse representation
    b[0][0] = 3;
    b[0][1] = 3;
    k = 1;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (B[i][j] != 0) {
                b[k][0] = i;
                b[k][1] = j;
                b[k][2] = B[i][j]; // Fixed: was A[i][j]
                k++;
            }
        }
    }
    b[0][2] = k - 1; // Total non-zero elements in B

    // Add sparse matrices a and b
    sum[0][0] = 3;
    sum[0][1] = 3;
    int i = 1, j = 1;
    k = 1;

    while (i <= a[0][2] && j <= b[0][2]) {
        if (a[i][0] < b[j][0] || (a[i][0] == b[j][0] && a[i][1] < b[j][1])) {
            sum[k][0] = a[i][0];
            sum[k][1] = a[i][1];
            sum[k][2] = a[i][2];
            i++;
            k++;
        } else if (b[j][0] < a[i][0] || (b[j][0] == a[i][0] && b[j][1] < a[i][1])) {
            sum[k][0] = b[j][0];
            sum[k][1] = b[j][1];
            sum[k][2] = b[j][2];
            j++;
            k++;
        } else {
            int added_val = a[i][2] + b[j][2];
            if (added_val != 0) {
                sum[k][0] = a[i][0];
                sum[k][1] = a[i][1];
                sum[k][2] = added_val;
                k++;
            }
            i++;
            j++;
        }
    }

    // Copy remaining elements of a
    while (i <= a[0][2]) {
        sum[k][0] = a[i][0];
        sum[k][1] = a[i][1];
        sum[k][2] = a[i][2];
        i++;
        k++;
    }

    // Copy remaining elements of b
    while (j <= b[0][2]) {
        sum[k][0] = b[j][0];
        sum[k][1] = b[j][1];
        sum[k][2] = b[j][2];
        j++;
        k++;
    }

    sum[0][2] = k - 1; // Total non-zero elements in sum

    // Print result
    printf("Addition in sparse representation\n");
    printf("Row Column Values\n");
    for (int r = 0; r <= sum[0][2]; r++) {
        printf("%d   %d      %d\n", sum[r][0], sum[r][1], sum[r][2]);
    }

    return 0;
}