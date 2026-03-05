import random
import math 
from typing import Tuple,NamedTuple

class MathTask(NamedTuple):
    problem:str
    solution:str
    hint: str  

def addition(max_add:int, max_sum:int):
    capped_num = min(max_add,max_sum)
    num1 = random.randint(1,capped_num)
    num2 = random.randint(min(1,max_sum - num1), capped_num)
    return MathTask(
            problem = f"{num1}+{num2}",
            solution = num1+num2,
            hint=f"Add {num1} and {num2} together to get the total.")

def subtraction(max_sub:int, max_diff:int):
    
    num1 = random.randint(1, max_sub)
    num2 = random.randint(max(1, (num1 - max_diff)), num1)
    return MathTask(
            problem = f"{num1}-{num2}",
            solution = num1-num2,
            hint=f"Start with {num1} and take away {num2}.")

def multiplication(max_multi:int):
   
    num1 = random.randint(1, max_multi)
    num2 = random.randint(1, max_multi)
    mul = num1 * num2

    return MathTask(
        problem=f'{num1}X{num2}',
        solution= f'{mul}',
        hint=f"Think of this as {num1} groups of {num2}."
    )

def division(max_num1:int, max_num2:int):

    num1 = random.randint(1, max_num1)
    num2 = random.randint(1, max_num2)

    divisor = num1 * num2
    dividend = random.choice([num1, num2])
    quotient = int(divisor / dividend)
    return MathTask(
        problem=f'{divisor}X{dividend}',
        solution= f'{quotient}',
        hint=f"How many times does {dividend} fit into {divisor}?"
    )

def algebra_basic(max_val: int):
    x = random.randint(1, max_val)
    const = random.randint(1, 10)
    res = x + const
    return MathTask(
        problem=f"x + {const} = {res}",
        solution=str(x),
        hint=f"To find x, subtract {const} from {res}.")

def geometry_area(max_val: int):
    l, w = random.randint(1, max_val), random.randint(1, max_val)
    return MathTask(
        problem=f"Rectangle with Length={l}, Width={w}. Area?", 
        solution=str(l*w),
        hint=f"Multiply length ({l}) by width ({w}) to find the area.")

def percentage_basic():
    pct = random.choice([10, 20, 25, 50])
    num = random.randint(1, 10) * 10
    ans = (pct / 100) * num
    return MathTask(
        problem=f"{pct}% of {num}",
        solution= str(int(ans)),
        hint=f"Divide {pct} by 100 and multiply by {num}.")

def geometry_pythagoras():
    # Standard triples like 3, 4, 5
    m = random.randint(1, 4)
    a, b, c = 3*m, 4*m, 5*m
    return MathTask(
        problem=f"Right triangle: a={a}, b={b}. Find c.", 
        solution=str(c),
        hint=f"Use the Pythagorean theorem: a² + b² = c².")

def trigonometry_basic():
    angle = random.choice([30, 45, 60])
    # Simplified for Grade 10 intro
    
    angle_rad = math.radians(angle)
    numerical_solution = round(math.sin(angle_rad), 3)

    return MathTask(
        problem=f"In a right triangle, what is the Sine of {angle}°?", 
        solution=str(numerical_solution),
        hint="Remember: sin(30°)=0.5, sin(90°)=1.0."
    )

def geometry_volume(max_val: int):
    l, w, h = random.randint(1, max_val), random.randint(1, max_val), random.randint(1, max_val)
    ans = l * w * h
    return MathTask(problem=f"Find the volume of a box with L={l}, W={w}, H={h}.", 
                    solution=str(ans),
                    hint=f"Volume is Length × Width × Height.")

def algebra_advanced(max_val: int):
    """
    Generates a two-step equation: ax + b = c
    Ensures x, a, and b are integers for Grade 9/10 clarity.
    """
    # 1. Generate the 'Truth' (the hidden x)
    x = random.randint(1, max_val // 5) 
    
    # 2. Generate the coefficients
    a = random.randint(2, 10)
    b = random.randint(1, 20)
    
    # 3. Calculate the result side
    # If the equation is ax + b = c, then c = (a * x) + b
    c = (a * x) + b
    
    problem = f"{a}x + {b} = {c}"
    solution = str(x)
    
    # # 4. Provide a detailed hint for the AI to follow
    # hint = (f"Step 1: Subtract {b} from both sides ({c} - {b} = {c-b}). "
    #         f"Step 2: Divide by {a} ({c-b} / {a} = {x}).")
    
    return MathTask(problem=problem, 
                    solution=solution,
                    hint ='(c-b)/a=x')#(f"({c-b} / {a} = {x})."))
def quadratic_simple():
    """
    Generates a quadratic equation: x² + bx + c = 0
    where the roots are simple integers.
    """
    # 1. Start with the roots (the answers)
    # We use small integers so the mental math isn't too hard
    root1 = random.randint(-10, 10)
    root2 = random.randint(-10, 10)
    
    # 2. Work backward to find b and c
    # Equation: (x - root1)(x - root2) = 0
    # x² - (root1 + root2)x + (root1 * root2) = 0
    b = -(root1 + root2)
    c = root1 * root2
    
    # 3. Format the problem string nicely
    # Handle the plus/minus signs for 'b' and 'c'
    b_sign = "+" if b >= 0 else "-"
    c_sign = "+" if c >= 0 else "-"
    
    problem = f"Solve for x: x² {b_sign} {abs(b)}x {c_sign} {abs(c)} = 0"
    solution = f"x = {root1}, {root2}"
    
    return MathTask(problem=problem, 
                    solution=solution,
                    hint = (f"Find two numbers that multiply to {c} and add up to {b}. "
            f"The factors are (x - {root1}) and (x - {root2})."))


MATH_CONFIG = {
    #grade 1: small numbers (0-10)
    1:[lambda:addition(max_add=10,max_sum=20),
        lambda: subtraction(max_sub=10, max_diff=10)],
    #grade 2:  upto 50 (0-10)
    2:[lambda: addition(max_add=50,max_sum=100),
        lambda: subtraction(max_sub=50, max_diff=50)],
    #grade 3: Intro to Multiplication & Division
    3:[lambda: addition(max_add=100,max_sum=200),
    lambda: subtraction(max_sub=100, max_diff=100),
    lambda: multiplication(10)],
    
    # Grade 4: Larger Multiplication & Division
    4: [
        lambda:  multiplication(max_multi=20),
        lambda:  division(max_num1=12, max_num2=12),
        lambda:  subtraction(max_sub=500, max_diff=500)
    ],
    # Grade 5: Geometry & Basic Percentages
    5: [
        lambda:  geometry_area(max_val=15),
        lambda:  percentage_basic(),
        lambda:  multiplication(max_multi=50)
    ],
    # Grade 6: Pre-Algebra (Solving for X)
    6: [
        lambda:  algebra_basic(max_val=20),
        lambda:  geometry_volume(max_val=10),
        lambda:  division(max_num1=25, max_num2=10)
    ],
    # Grade 7: Ratios & Integers
    7: [
        lambda:  algebra_basic(max_val=50),
        lambda:  percentage_basic(),
        lambda:  geometry_area(max_val=50)
    ],
    # Grade 8: Linear Equations & Geometry
    8: [
        lambda:  algebra_basic(max_val=100),
        lambda:  geometry_pythagoras(),
        lambda:  geometry_volume(max_val=20)
    ],
    # Grade 9: Advanced Algebra (Polynomials/Squares)
    9: [
        lambda:  algebra_advanced(max_val=200),
        lambda:  geometry_pythagoras(),
        lambda:  percentage_basic()
    ],
    # Grade 10: Trigonometry & Quadratics
    10: [
        lambda:  trigonometry_basic(),
        lambda:  quadratic_simple(),
        lambda:  algebra_advanced(max_val=500)
    ]
}
