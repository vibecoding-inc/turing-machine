#!/usr/bin/env python3
"""
Main program for Turing Machine Executor

This program allows users to define and execute Turing machines interactively.
"""

import json
import sys
from turing_machine import TuringMachine, create_example_machines


def print_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("TURING MACHINE EXECUTOR")
    print("=" * 60)
    print("1. Run example machine")
    print("2. Define custom machine (JSON format)")
    print("3. Load machine from file")
    print("4. Help")
    print("5. Exit")
    print("=" * 60)


def print_help():
    """Display help information."""
    print("\n" + "=" * 60)
    print("HELP - Turing Machine Format")
    print("=" * 60)
    print("""
A Turing machine is defined using JSON with the following structure:

{
    "states": ["q0", "q1", "accept", "reject"],
    "alphabet": ["0", "1"],
    "tape_alphabet": ["0", "1", "_"],
    "initial_state": "q0",
    "accept_states": ["accept"],
    "reject_states": ["reject"],
    "blank_symbol": "_",
    "transitions": {
        "q0,0": ["q0", "0", "R"],
        "q0,1": ["q1", "1", "R"],
        "q1,_": ["accept", "_", "R"]
    }
}

Transition format: "state,symbol": [new_state, write_symbol, direction]
Direction: "L" (left), "R" (right)

The program will:
1. Execute the machine on your input string
2. Report if it ACCEPTS or REJECTS (holds)
3. Show the final state reached
""")


def parse_machine_json(json_data):
    """
    Parse a Turing machine from JSON format.
    
    Args:
        json_data: Dict containing machine definition
        
    Returns:
        TuringMachine instance
    """
    # Parse transitions from string keys to tuple keys
    transitions = {}
    for key, value in json_data['transitions'].items():
        state, symbol = key.split(',')
        transitions[(state, symbol)] = tuple(value)
    
    return TuringMachine(
        states=set(json_data['states']),
        alphabet=set(json_data['alphabet']),
        tape_alphabet=set(json_data['tape_alphabet']),
        transitions=transitions,
        initial_state=json_data['initial_state'],
        accept_states=set(json_data['accept_states']),
        reject_states=set(json_data['reject_states']),
        blank_symbol=json_data.get('blank_symbol', '_')
    )


def run_example_machine():
    """Run one of the predefined example machines."""
    examples = create_example_machines()
    
    print("\n" + "=" * 60)
    print("EXAMPLE MACHINES")
    print("=" * 60)
    print("1. Even number of 1s (accepts strings with even number of 1s)")
    print("2. Equal 0s and 1s (accepts 0^n 1^n where n >= 1)")
    print("3. Accept all (accepts any string)")
    print("=" * 60)
    
    choice = input("\nSelect example (1-3): ").strip()
    
    machine_map = {
        '1': ('even_ones', 'Even number of 1s'),
        '2': ('equal_zeros_ones', 'Equal 0s and 1s (0^n 1^n)'),
        '3': ('accept_all', 'Accept all strings')
    }
    
    if choice not in machine_map:
        print("Invalid choice!")
        return
    
    machine_key, machine_name = machine_map[choice]
    machine = examples[machine_key]
    
    print(f"\nSelected: {machine_name}")
    print("-" * 60)
    
    while True:
        input_str = input("\nEnter input string (or 'back' to return): ").strip()
        if input_str.lower() == 'back':
            break
        
        try:
            result = machine.execute(input_str)
            
            print("\n" + "-" * 60)
            print("EXECUTION RESULTS")
            print("-" * 60)
            print(f"Input string: '{input_str}'")
            print(f"Steps executed: {result['steps']}")
            print(f"Final state: {result['final_state']}")
            print(f"Machine halted: {result['halted']}")
            
            if result['accepts'] is True:
                print(f"\n✓ RESULT: ACCEPTS (holds in state {result['final_state']})")
            elif result['accepts'] is False:
                print(f"\n✗ RESULT: REJECTS (final state: {result['final_state']})")
            else:
                print(f"\n? RESULT: DID NOT HALT (possible infinite loop)")
            print("-" * 60)
            
        except ValueError as e:
            print(f"Error: {e}")


def run_custom_machine():
    """Allow user to define a custom Turing machine via JSON."""
    print("\n" + "=" * 60)
    print("DEFINE CUSTOM MACHINE (JSON)")
    print("=" * 60)
    print("Enter JSON definition (type 'help' for format, 'cancel' to abort):")
    print("You can enter it as a single line or multiple lines (end with empty line)")
    print("-" * 60)
    
    lines = []
    while True:
        line = input()
        if line.strip().lower() == 'cancel':
            return
        if line.strip().lower() == 'help':
            print_help()
            print("Continue entering JSON:")
            continue
        if not line.strip() and lines:
            break
        if line.strip():
            lines.append(line)
    
    json_str = '\n'.join(lines)
    
    try:
        json_data = json.loads(json_str)
        machine = parse_machine_json(json_data)
        
        print("\n✓ Machine created successfully!")
        print(f"States: {len(machine.states)}")
        print(f"Transitions: {len(machine.transitions)}")
        
        while True:
            input_str = input("\nEnter input string (or 'back' to return): ").strip()
            if input_str.lower() == 'back':
                break
            
            try:
                result = machine.execute(input_str)
                
                print("\n" + "-" * 60)
                print("EXECUTION RESULTS")
                print("-" * 60)
                print(f"Input string: '{input_str}'")
                print(f"Steps executed: {result['steps']}")
                print(f"Final state: {result['final_state']}")
                print(f"Machine halted: {result['halted']}")
                
                if result['accepts'] is True:
                    print(f"\n✓ RESULT: ACCEPTS (holds in state {result['final_state']})")
                elif result['accepts'] is False:
                    print(f"\n✗ RESULT: REJECTS (final state: {result['final_state']})")
                else:
                    print(f"\n? RESULT: DID NOT HALT (possible infinite loop)")
                print("-" * 60)
                
            except ValueError as e:
                print(f"Error: {e}")
    
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
    except Exception as e:
        print(f"Error creating machine: {e}")


def load_machine_from_file():
    """Load a Turing machine definition from a JSON file."""
    print("\n" + "=" * 60)
    print("LOAD MACHINE FROM FILE")
    print("=" * 60)
    
    filename = input("Enter filename (or 'cancel' to abort): ").strip()
    if filename.lower() == 'cancel':
        return
    
    try:
        with open(filename, 'r') as f:
            json_data = json.load(f)
        
        machine = parse_machine_json(json_data)
        
        print("\n✓ Machine loaded successfully!")
        print(f"States: {len(machine.states)}")
        print(f"Transitions: {len(machine.transitions)}")
        
        while True:
            input_str = input("\nEnter input string (or 'back' to return): ").strip()
            if input_str.lower() == 'back':
                break
            
            try:
                result = machine.execute(input_str)
                
                print("\n" + "-" * 60)
                print("EXECUTION RESULTS")
                print("-" * 60)
                print(f"Input string: '{input_str}'")
                print(f"Steps executed: {result['steps']}")
                print(f"Final state: {result['final_state']}")
                print(f"Machine halted: {result['halted']}")
                
                if result['accepts'] is True:
                    print(f"\n✓ RESULT: ACCEPTS (holds in state {result['final_state']})")
                elif result['accepts'] is False:
                    print(f"\n✗ RESULT: REJECTS (final state: {result['final_state']})")
                else:
                    print(f"\n? RESULT: DID NOT HALT (possible infinite loop)")
                print("-" * 60)
                
            except ValueError as e:
                print(f"Error: {e}")
    
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in file: {e}")
    except Exception as e:
        print(f"Error loading machine: {e}")


def main():
    """Main program loop."""
    print("\nWelcome to the Turing Machine Executor!")
    print("This program allows you to execute Turing machines and determine:")
    print("  1. If the machine accepts/rejects the input (holds)")
    print("  2. The final state reached by the machine")
    
    while True:
        print_menu()
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            run_example_machine()
        elif choice == '2':
            run_custom_machine()
        elif choice == '3':
            load_machine_from_file()
        elif choice == '4':
            print_help()
        elif choice == '5':
            print("\nThank you for using the Turing Machine Executor!")
            sys.exit(0)
        else:
            print("Invalid choice! Please select 1-5.")


if __name__ == '__main__':
    main()
