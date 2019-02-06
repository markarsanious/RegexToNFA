import argparse

class NFA:
    def __init__(self, initial_state, final_state, states, transitions):
        self.initial_state = initial_state
        self.final_state = final_state
        self.states = states
        self.transitions = transitions

    # create a new transition from a specific state to the new states with the specified condition
    # add this new transition to the old transitions
    def create_transition(self, from_state, to_states, condition):
        for transition in self.transitions:
            if transition['from_state'] == from_state and transition['condition'] == condition:
                transition['to_states'] += to_states
                return
        new_transition = dict()
        new_transition['from_state'] = from_state
        new_transition['to_states'] = to_states
        new_transition['condition'] = condition
        self.transitions.append(new_transition)

    def display(self):
        print(",".join(self.states))
        print(",".join(set(alphabet)))
        print(self.initial_state)
        print(self.final_state)
        print(self.display_transitions())

    def display_transitions(self):
        transitions_string = ""
        for transition in self.transitions:
            transitions_string += "(" + transition['from_state'] +", " + transition['condition'] +", " + str(transition['to_states']) + "), "
        return transitions_string[:len(transitions_string)-2]


def resolve_duplicate_states(x, old_y):
    global states_counter
    replace_states = False
    new_y_states = []
    for index, state in enumerate(old_y.states):
        new_y_states.append(state)
    new_y = NFA(old_y.initial_state, old_y.final_state, new_y_states, [])

    for transition in old_y.transitions:
        transition_to_states = []
        for index, to_state in enumerate(transition['to_states']):
            transition_to_states.append(to_state)
        new_y.create_transition(transition['from_state'], transition_to_states , transition['condition'])

    for y_state in old_y.states:
        for x_state in x.states:
            if x_state == y_state:
                replace_states = True
                break
        if replace_states:
            break

    if replace_states:
        for index, state in enumerate(new_y.states):
            states_counter += 1
            replacement_state = "s" + str(states_counter)
            new_y.states[index] = replacement_state

            if new_y.initial_state == state:
                new_y.initial_state = replacement_state

            if new_y.final_state == state:
                new_y.final_state = replacement_state

            for transition_index, transition in enumerate(old_y.transitions):
                if transition['from_state'] == state:
                    new_y.transitions[transition_index]['from_state'] = replacement_state

                for to_state_index, to_state in enumerate(transition['to_states']):
                    if to_state == state:
                        new_y.transitions[transition_index]['to_states'][to_state_index] = replacement_state
    return x, new_y


def concat(x, y):
    x, new_y = resolve_duplicate_states(x, y)
    new_x = NFA(x.initial_state, new_y.initial_state, [], [])
    new_x.states = [state for state in x.states]
    new_x.states.remove(x.final_state)
    new_x.transitions = x.transitions.copy()

    for i, transition in enumerate(new_x.transitions):
        if new_x.transitions[i]['from_state'] == x.final_state:
            new_x.transitions[i]['from_state'] = new_y.initial_state
        for j, to_state in enumerate(new_x.transitions[i]['to_states']):
            if new_x.transitions[i]['to_states'][j] == x.final_state:
                new_x.transitions[i]['to_states'][j] = new_y.initial_state

    new_nfa = NFA(new_x.initial_state, new_y.final_state, new_x.states + new_y.states, [])
    for x_transition in new_x.transitions:
        new_nfa.create_transition(x_transition['from_state'], x_transition['to_states'], x_transition['condition'])
    for y_transition in new_y.transitions:
        new_nfa.create_transition(y_transition['from_state'], y_transition['to_states'], y_transition['condition'])
    # new_nfa.create_transition(x.final_state, [new_y.initial_state], " ")
    return new_nfa

def union(x, y):
    x, new_y = resolve_duplicate_states(x, y)
    global states_counter
    states_counter +=1
    new_initial_state = "s"+str(states_counter)
    states_counter +=1
    new_final_state = "s"+str(states_counter)
    new_nfa = NFA(new_initial_state, new_final_state, x.states + y.states + [new_initial_state, new_final_state], [])
    new_nfa.transitions = x.transitions + y.transitions
    new_nfa.create_transition(new_initial_state, [x.initial_state], " ")
    new_nfa.create_transition(new_initial_state, [y.initial_state], " ")
    new_nfa.create_transition(x.final_state, [new_final_state], " ")
    new_nfa.create_transition(y.final_state, [new_final_state], " ")
    return new_nfa

def kleene(x):
    global states_counter
    states_counter +=1
    new_initial_state = "s"+str(states_counter)
    states_counter +=1
    new_final_state = "s"+str(states_counter)
    new_nfa = NFA(new_initial_state, new_final_state, x.states + [new_initial_state, new_final_state], [])
    for transition in x.transitions:
        new_nfa.create_transition(transition['from_state'], transition['to_states'], transition['condition'])
    new_nfa.create_transition(new_initial_state, [x.initial_state], " ")
    new_nfa.create_transition(new_initial_state, [new_final_state], " ")
    new_nfa.create_transition(x.final_state, [new_final_state], " ")
    new_nfa.create_transition(x.final_state, [x.initial_state], " ")
    return new_nfa


def plus(x):
    return concat(x, kleene(x))

def one_action(condition):
    global states_counter
    states_counter += 1
    state_1 = "s" + str(states_counter)
    states_counter += 1
    state_2 = "s" + str(states_counter)
    new_nfa = NFA(state_1, state_2, [state_1, state_2], [])
    new_nfa.create_transition(state_1, [state_2], condition)
    return new_nfa

def question_mark(x):
    global states_counter
    states_counter += 1
    new_initial_state = "s" + str(states_counter)
    states_counter += 1
    new_final_state = "s" + str(states_counter)
    new_nfa = NFA(new_initial_state, new_final_state, x.states + [new_initial_state, new_final_state], [])
    for transition in x.transitions:
        new_nfa.create_transition(transition['from_state'], transition['to_states'], transition['condition'])
    new_nfa.create_transition(new_initial_state, [x.initial_state], " ")
    new_nfa.create_transition(new_initial_state, [new_final_state], " ")
    new_nfa.create_transition(x.final_state, [new_final_state], " ")
    return new_nfa

#compare precdence of two operators
def compare_precedence(x, y):
    left = 0
    right = 0
    if x == "*" or x == "+" or x == "?":
        left = 3
    if x == ".":
        left = 2
    if x == "|":
        left = 1
    if y == "*" or y == "+" or y == "?":
        right = 3
    if y == ".":
        right = 2
    if y == "|":
        right = 1

    return left - right

#Highest: *,+,?, lower: concat, lowest: union
#if operand, add it in postfix string
#if operator and stack is empty/left paranthesis on top: push it on top of stack
#if ( push it on stack
#if ) pop and print to postfix string until you find ( , discard the brackets
#if operator with higher precedence, push it on stack
#if equal precedence, pop and print top of stack then push the operator on stack
#if lower precedence, pop& print and re-test
#at end, pop all operators
def infix_to_postfix(infix):
    #initialize empty postfix string
    postfix = ""
    stack = []
    for c in infix:
        #if it is an operand, add it directly to postfix string
        if not (c == "*" or c == "+" or c == "?" or c == "." or c == "|" or c == "(" or c == ")"):
            postfix += c
        #if stack is empty or top is ( , print it to postfix string
        elif len(stack)== 0 or stack[len(stack)-1]=="(":
            stack.append(c)
        #if left bracket, push it on stack
        elif c == "(":
            stack.append(c)
        #if ) pop until you find (
        elif c == ")":
            while(not (stack[len(stack)-1] == "(")):
                popped = stack[len(stack)-1]
                postfix += popped
                stack = stack[:len(stack)-1]
            stack = stack[:len(stack)-1]
        #if c has higher precedence than top of stack, push it on top of stack
        elif compare_precedence(c, stack[len(stack)-1]) > 0:
            stack.append(c)
        #if equal precedence, pop one element from stack and push c
        elif compare_precedence(c, stack[len(stack)-1]) == 0:
            popped = stack[len(stack)-1]
            postfix += popped
            stack[len(stack)-1] = c
        #if lower precedence, pop and print until otherwise
        elif compare_precedence(c, stack[len(stack)-1]) < 0:
            while (len(stack) > 0) and not (stack[len(stack)-1] == "(") and (compare_precedence(c, stack[len(stack)-1]) < 0):
                popped = stack[len(stack)-1]
                postfix += popped
                stack = stack[:len(stack)-1]
            if len(stack) > 0 and not (stack[len(stack)-1] == "(") and (compare_precedence(c, stack[len(stack) - 1]) == 0):
                popped = stack[len(stack) - 1]
                postfix += popped
                stack = stack[: len(stack) - 1]
            stack.append(c)

    #if infix string is over, pop all stack and print it to postix
    while(not (len(stack) == 0)):
        popped = stack[len(stack)-1]
        postfix += popped
        stack = stack[:len(stack)-1]

    return postfix


def modifyRegex(regex):
    index = 0
    while index < len(regex):
        #replace all epsilons with spaces
        regex = regex.replace("ε", " ")
        #add . as concatenation operator in all the needed locations
        if index > 0 and not (regex[index] == ")" or regex[index-1] == "(" or regex[index-1] == "|" or regex[index] == "|" or regex[index] == "*" or regex[index] == "+" or regex[index] == "?"):
            regex = regex[0:index] + "." + regex[index:]
            index +=1
        index += 1
    return regex

#continuously parse the postfix string until it is finished
#everytime you parse an operator, pop 1 or 2 operands (depending on the operator),
# perform the operation and push it on top of stack
def transformToNFA(postfix):
    global alphabet
    stack = []
    for c in postfix:
        if c == ".":
            x = stack[len(stack) - 2]
            y = stack[len(stack) - 1]
            stack = stack[:len(stack) - 2]
            z = concat(x, y)
            stack.append(z)
        elif c == "|":
            x = stack[len(stack) - 2]
            y = stack[len(stack) - 1]
            stack = stack[:len(stack) - 2]
            z = union(x, y)
            stack.append(z)
        elif c == "*":
            x = stack[len(stack) - 1]
            stack = stack[:len(stack) - 1]
            z = kleene(x)
            stack.append(z)
        elif c == "+":
            x = stack[len(stack) - 1]
            stack = stack[:len(stack) - 1]
            z = plus(x)
            stack.append(z)
        elif c == "?":
            x = stack[len(stack) - 1]
            stack = stack[:len(stack) - 1]
            z = question_mark(x)
            stack.append(z)
        else:
            alphabet.append(c)
            x = one_action(c)
            stack.append(x)
    return stack

#-------------------RUN CODE----------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",
                        metavar="file")

    args = parser.parse_args()
    print(args.file)

    output_file = open("task_2_result.txt", "w+")

    with open(args.file, "r") as file:
        for line in file:
            # initialize global variables
            regex = line
            states_counter = 0
            alphabet = []

            # input regex, modify it to replace epsilon with space and add "." to represent concatenation
            # then, transform the infix notation to postfix and run the code to transform it to NFA
            # regex = "(0|(1(01*(00)*0)*1)*)*"
            regex = modifyRegex(regex)
            postfix = infix_to_postfix(regex)
            stack = transformToNFA(postfix)
            # stack[0].display()

            # write the output of the result NFA in the output file with the specified format
            output_file.write(",".join(stack[0].states) + "\n")
            output_file.write(",".join(set(alphabet)) + "\n")
            output_file.write(stack[0].initial_state + "\n")
            output_file.write(stack[0].final_state + "\n")
            output_file.write(stack[0].display_transitions() + "\n")
            output_file.write("\n")


