#!/usr/bin/env python3
"""
Turing Machine Executor

This module provides a Turing machine implementation that can execute
user-defined Turing machines and determine:
1. If the machine accepts/rejects (holds)
2. The final state of the machine
"""

class TuringMachine:
    """
    A Turing machine executor.
    
    The machine consists of:
    - A tape (infinite in both directions)
    - A head that can read/write symbols and move left/right
    - A finite set of states
    - A transition function
    - An initial state
    - A set of accept states
    - A set of reject states
    """
    
    def __init__(self, states, alphabet, tape_alphabet, transitions, 
                 initial_state, accept_states, reject_states, blank_symbol='_'):
        """
        Initialize a Turing machine.
        
        Args:
            states: Set of state names
            alphabet: Input alphabet (symbols that can appear in input)
            tape_alphabet: Tape alphabet (includes alphabet + blank + work symbols)
            transitions: Dict mapping (state, symbol) -> (new_state, write_symbol, direction)
                        direction is 'L' for left, 'R' for right
            initial_state: Starting state
            accept_states: Set of accepting states
            reject_states: Set of rejecting states
            blank_symbol: Symbol representing blank tape cells (default '_')
        """
        self.states = states
        self.alphabet = alphabet
        self.tape_alphabet = tape_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.accept_states = accept_states
        self.reject_states = reject_states
        self.blank_symbol = blank_symbol
        
        # Validate input
        if initial_state not in states:
            raise ValueError(f"Initial state {initial_state} not in states")
        if not accept_states.issubset(states):
            raise ValueError("Accept states must be subset of states")
        if not reject_states.issubset(states):
            raise ValueError("Reject states must be subset of states")
        if not accept_states.isdisjoint(reject_states):
            raise ValueError("Accept and reject states must be disjoint")
            
    def execute(self, input_string, max_steps=10000):
        """
        Execute the Turing machine on the given input.
        
        Args:
            input_string: Input string to process
            max_steps: Maximum number of steps before assuming infinite loop
            
        Returns:
            dict with keys:
                'accepts': True if machine accepts, False if rejects, None if loops
                'final_state': The final state reached
                'steps': Number of steps executed
                'halted': Whether the machine halted
        """
        # Initialize tape with input
        tape = list(input_string) if input_string else [self.blank_symbol]
        head_position = 0
        current_state = self.initial_state
        steps = 0
        
        # Ensure all input symbols are valid
        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f"Invalid input symbol: {symbol}")
        
        # Execute until halt or max steps
        while steps < max_steps:
            # Check if in halting state
            if current_state in self.accept_states:
                return {
                    'accepts': True,
                    'final_state': current_state,
                    'steps': steps,
                    'halted': True,
                    'tape': ''.join(tape)
                }
            
            if current_state in self.reject_states:
                return {
                    'accepts': False,
                    'final_state': current_state,
                    'steps': steps,
                    'halted': True,
                    'tape': ''.join(tape)
                }
            
            # Extend tape if needed
            if head_position < 0:
                tape.insert(0, self.blank_symbol)
                head_position = 0
            if head_position >= len(tape):
                tape.append(self.blank_symbol)
            
            # Read current symbol
            current_symbol = tape[head_position]
            
            # Look up transition
            transition_key = (current_state, current_symbol)
            if transition_key not in self.transitions:
                # No transition defined - implicit reject
                return {
                    'accepts': False,
                    'final_state': current_state,
                    'steps': steps,
                    'halted': True,
                    'tape': ''.join(tape)
                }
            
            # Apply transition
            new_state, write_symbol, direction = self.transitions[transition_key]
            
            # Write symbol
            tape[head_position] = write_symbol
            
            # Move head
            if direction == 'L':
                head_position -= 1
            elif direction == 'R':
                head_position += 1
            else:
                raise ValueError(f"Invalid direction: {direction}")
            
            # Update state
            current_state = new_state
            steps += 1
        
        # Max steps reached - likely infinite loop
        return {
            'accepts': None,
            'final_state': current_state,
            'steps': steps,
            'halted': False,
            'tape': ''.join(tape)
        }


def create_example_machines():
    """
    Create some example Turing machines for testing.
    
    Returns:
        dict: Dictionary of example machines
    """
    examples = {}
    
    # Machine 1: Accepts strings with even number of 1s
    examples['even_ones'] = TuringMachine(
        states={'q0', 'q1', 'accept', 'reject'},
        alphabet={'0', '1'},
        tape_alphabet={'0', '1', '_'},
        transitions={
            ('q0', '0'): ('q0', '0', 'R'),
            ('q0', '1'): ('q1', '1', 'R'),
            ('q0', '_'): ('accept', '_', 'R'),
            ('q1', '0'): ('q1', '0', 'R'),
            ('q1', '1'): ('q0', '1', 'R'),
            ('q1', '_'): ('reject', '_', 'R'),
        },
        initial_state='q0',
        accept_states={'accept'},
        reject_states={'reject'}
    )
    
    # Machine 2: Accepts strings of the form 0^n 1^n (n >= 1)
    examples['equal_zeros_ones'] = TuringMachine(
        states={'q0', 'q1', 'q2', 'q3', 'q4', 'accept', 'reject'},
        alphabet={'0', '1'},
        tape_alphabet={'0', '1', 'X', 'Y', '_'},
        transitions={
            # Start: mark first 0
            ('q0', '0'): ('q1', 'X', 'R'),
            ('q0', '_'): ('reject', '_', 'R'),
            ('q0', '1'): ('reject', '1', 'R'),
            
            # Move right to find first 1
            ('q1', '0'): ('q1', '0', 'R'),
            ('q1', 'Y'): ('q1', 'Y', 'R'),
            ('q1', '1'): ('q2', 'Y', 'L'),
            ('q1', '_'): ('reject', '_', 'R'),
            
            # Move left back to start
            ('q2', '0'): ('q2', '0', 'L'),
            ('q2', 'Y'): ('q2', 'Y', 'L'),
            ('q2', 'X'): ('q0', 'X', 'R'),
            
            # Check if all matched
            ('q0', 'X'): ('q3', 'X', 'R'),
            ('q3', 'X'): ('q3', 'X', 'R'),
            ('q3', 'Y'): ('q3', 'Y', 'R'),
            ('q3', '_'): ('accept', '_', 'R'),
        },
        initial_state='q0',
        accept_states={'accept'},
        reject_states={'reject'}
    )
    
    # Machine 3: Simple acceptor - accepts any string
    examples['accept_all'] = TuringMachine(
        states={'q0', 'accept'},
        alphabet={'0', '1', 'a', 'b'},
        tape_alphabet={'0', '1', 'a', 'b', '_'},
        transitions={
            ('q0', '0'): ('q0', '0', 'R'),
            ('q0', '1'): ('q0', '1', 'R'),
            ('q0', 'a'): ('q0', 'a', 'R'),
            ('q0', 'b'): ('q0', 'b', 'R'),
            ('q0', '_'): ('accept', '_', 'R'),
        },
        initial_state='q0',
        accept_states={'accept'},
        reject_states=set()
    )
    
    return examples


if __name__ == '__main__':
    # Example usage
    print("Turing Machine Executor - Examples\n")
    
    examples = create_example_machines()
    
    # Test even ones machine
    print("=" * 60)
    print("Machine: Even number of 1s")
    print("=" * 60)
    machine = examples['even_ones']
    
    test_cases = ['', '0', '1', '11', '101', '111', '0101', '1111']
    for test in test_cases:
        result = machine.execute(test)
        print(f"Input: '{test}' -> ", end="")
        if result['accepts']:
            print(f"ACCEPTS (state: {result['final_state']}, steps: {result['steps']})")
        else:
            print(f"REJECTS (state: {result['final_state']}, steps: {result['steps']})")
    
    print("\n" + "=" * 60)
    print("Machine: Accept all strings")
    print("=" * 60)
    machine = examples['accept_all']
    
    test_cases = ['', 'ab', '01010', '111']
    for test in test_cases:
        result = machine.execute(test)
        print(f"Input: '{test}' -> ", end="")
        if result['accepts']:
            print(f"ACCEPTS (state: {result['final_state']}, steps: {result['steps']})")
        else:
            print(f"REJECTS (state: {result['final_state']}, steps: {result['steps']})")
