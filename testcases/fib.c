#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

long long fib(int n) {
    long long result, a, b;

    if (n <= 1) result = 1;
    else
    {
        #pragma omp task shared(a)
        a = fib(n - 1);
        b = fib(n - 2);
        #pragma omp taskwait

        result = a + b;
    }
    return result;
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
