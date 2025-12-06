#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

long long fib(int n) {
    if (n <= 1) return 1;

    long long a, b;

    #pragma omp task shared(a) if(n > 20)
    a = fib(n - 1);

    b = fib(n - 2);

    #pragma omp taskwait
    return a + b;
}

int main(int argc, char** argv) {
    if (argc < 1) return 1;

    int n = atoi(argv[1]);
    long long result;

    #pragma omp parallel
    {
        #pragma omp single
        {
            result = fib(n);
        }
    }

    printf("fib(%d) = %lld\n", n, result);
    return 0;
}
