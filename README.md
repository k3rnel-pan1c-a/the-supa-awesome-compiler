# Marsh

A very cool compiler for a very cool language written using python and LLVM!! 

 ## Features
- **it's fast**, because it should be so, together with LLVM's state of the art optimizations, but it won't ever oblige you to make an extra effort from your side just for the sake of performance
- **it's compiled** using llvmlite
- **it's statically typed** so you don't need to guess the type of the variable if your coworker didn't spend the time to use meaningful names and you can make use of compile-time checks, autocomplete and more


## Factorial Function

```
function fact(n: int) -> int{
    if n == 1{
        return 1;
    }
    return n * fact(n-1);
}

function main() -> int{
    return fact(5);
}

```

## Binary Search
```
function main() -> int{
    let element: int = 4;
    let low: int = 0;
    let high: int = 4;

    let arr: [int, 10] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    while low <= high{
        let mid: int = low + (high - low) / 2;

        if arr[mid] == element{
            return mid;
        }
        if arr[mid] < element{
            low = mid + 1;
        }
        else{
            high = mid - 1;
        }

    }

    return 1;
}
```


## Conditionals
Implemented if-else statements
```
function main() -> int{
    let x: int = 5;

    if x == 5{
        x = x + 1;
    }
    else{
        x = x - 1;
    }
    return x;

}
```

## While Loops
Implemented standard while loops
```
function main() -> int{
    let x: int = 0;
    
    while x <= 10{
        x = x + 1;
    }

    return x;
}

```

## For Loops
Implemented standard for loops
```
function main() -> int{
    let x: int = 0;

    for i in 1..200{
        x = x + i;
    }
    return x;
}
```

## Bitwise Operations
Common bitwise operations are implemented including: or (|), xor (^), and(&) and not(~)
```
function main() -> int{
    let x: int = 10;
    let y: int = 20;

    return x ^ y;
}
```

## Function Calls
```
function sum(x: int, y: int) -> int{
    return x + y;
}

function main() -> int{
    let x: int = 10;
    let y: int = 20;

    return sum(x, y);
}
```

