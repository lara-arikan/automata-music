#!/usr/bin/env python
# coding: utf-8

# In[20]:


from music21 import note, stream, alpha, audioSearch, configure
from tkinter import *
from tkinter.ttk import *


# In[21]:


def get_binary(number):
    return format(number, '08b')

def advance(ruleset, curr_gen): #curr_gen is binary string
    curr_gen = '0' + curr_gen + '0' # pad with zeros
    next_gen = ''
    for i in range(len(curr_gen)):
        curr_binary = int(curr_gen[i:i+3], base=2) #three-bit neighborhood
        next_gen += ruleset[len(ruleset) - 1 - curr_binary] #ruleset most significant bit on left

    return next_gen

def draw_generation(curr_gen):
    printable = ''
    for i in range(len(curr_gen)):
        if curr_gen[i] == '0':
            printable += ' '
        else:
            printable += '+'
            
    return printable 

def all_gens(ruleset, gen_0, n_gens):
    all_gens = [gen_0]
    curr_gen = gen_0
    for i in range(n_gens):
        new_gen = advance(ruleset, curr_gen)
        all_gens.append(new_gen)
        curr_gen = new_gen
    return all_gens

def all_freqs_linear(freq_min, freq_max, n_gens):
    f_unit = (freq_max - freq_min) // n_gens
    return [f_unit * i + freq_min for i in range(n_gens)]
    
def populate_stream(stream, freq, gen, mode): #fill stream by user specified mode
    for bit in gen:
        f = note.Note()
        f.duration.quarterLength = 0.5
        f.pitch.frequency = freq
        if mode == "rest" and bit == '0': # 0's are rests
            f.volume.velocity = 0
        elif mode == "low" and bit == '0':
            f.volume.velocity = 10
        else:
            f.volume.velocity = 90 # must be 1
        
        stream.append(f)
        
    return stream
        

def sonify_general(ruleset, gen_0, n_gens, n_streams, rest_mode, freq_min, freq_max):   
    if rest_mode == 0:
        rest_mode = "rest"
    else:
        rest_mode = "low"
        
    lastgens = ''
        
    ruleset = get_binary(ruleset)
    gen_0 = get_binary(gen_0)
    freqs = all_freqs_linear(freq_min, freq_max, n_gens)
    
    streams = [stream.Stream() for i in range(n_streams)] #initialize all streams
    gens = all_gens(ruleset, gen_0, n_gens)

    for i in range(n_gens // n_streams):
        curr_gens = gens[n_streams * i : n_streams * (i + 1)]
        fs = freqs[n_streams * i : n_streams * (i + 1)]
        for index, gen in enumerate(curr_gens):
            curr_stream = streams[index]
            curr_f = fs[index]
            curr_stream = populate_stream(curr_stream, curr_f, gen, rest_mode)
            lastgens += (draw_generation(gen) + '\n')
        
    for i, stream_i in enumerate(streams):
        filename = 's' + str(i) + '_' + str(ruleset) + '_' + str(n_gens)  + '_' + rest_mode + '.mid'
        stream_i.write("midi", filename)
    
    return lastgens


# In[22]:


# if user wants more info about inputs,

def info():
    num = choice.get()
    if num == 0:
        explain.config(text = """A number between 0 and 255. This will be converted to binary and used to determine the next generation given the current one. Interesting music comes from rulesets that cause periodic changes across generations. A few good numbers to start with are 60, graphically represented as the Sierpinski triangle; 77, a personal favorite; and 90, which relates to Pascal's triangle.""")
    elif num == 1:
        explain.config(text = "Will be converted to binary. No negative numbers!")
    elif num == 2:
        explain.config(text = "How many generations will be processed at a time. The program will save a number of midi files equal to the number of streams. These files should be layered to get the specified number of generations playing at once. Should evenly divide the number of generations.")
    elif num == 3:
        explain.config(text = "The number of generations you want to make music out of. More generations means longer midi tracks.")
    else:
        explain.config(text = "Within the bounds 30-3900. Put a hyphen (-) between your minimum and maximum frequencies, and write the minimum first.")

# if user wants more info about the options for a 0 bit,
        
def mode_inf():
    num = mode.get()
    if num == 0:
        explain.config(text = "The 0-bits in a generation will be silent. Good choice for many streams going at once.")
    else:
        explain.config(text = "The 0-bits in a generation will be assigned the same frequency as a 1-bit, at a lower volume.")

def activate():
    run["state"] = "disabled" # no more clicks; crashes otherwise
    
    rs = ruleset.get()
    gen0 = gen.get()
    ns = nstreams.get()
    ngs = ngens.get()
    rmode = mode.get()
    fminmax = fmaxmin.get()
    
    if not (len(rs) > 0 and len(gen0) > 0 and len(ngs) > 0 and len(fminmax) > 0 and rs.isdigit() and gen0.isdigit() and ngs.isdigit()):
        explain.config(text = """Fill every entry box before pressing Run.
                       Use only numbers, except for the hyphen between frequencies. Negative numbers are not allowed.""")
        run["state"] = 'normal' # allow running again
        return 0
    
    rs = int(rs) # these are all numbers as string input
    gen0 = int(gen0)
    ngs = int(ngs)
    ns = int(ns)
    
    if rs > 255 or gen0 > 1000000:
        explain.config(text = "Your ruleset must be smaller than 256. Your first generation should not be larger than 1,000,000.")
        run["state"] = 'normal'
        return 0
    
    if rs == 0 or gen0 == 0 or ngs == 0 or ns == 0:
        explain.config(text = "If you want to make music, no entry can be 0.")
        run["state"] = 'normal'
        return 0
    
    if not ngs % ns == 0:
        explain.config(text = "The number of generations must be an integer multiple of the number of streams.")
        run["state"] = 'normal'
        return 0
    
    if ns > 5:
        explain.config(text = "Too many streams... the program is given more than it wants to carry. Try less than five.")
        run["state"] = 'normal'
        return 0
    
    delim = fminmax.find('-')
    if delim == -1:
        explain.config(text = "You must use a hyphen between minimum and maximum frequencies.")
        run["state"] = 'normal'
        return 0
    
    fmin = fminmax[:delim]
    fmax = fminmax[delim + 1:]
    
    if not (fmin.isdigit() and fmax.isdigit()):
        explain.config(text = "Your frequencies must be composed only of digits, with a hyphen in between (e.g. 500-2000).")
        run["state"] = 'normal'
        return 0
    
    fmin = int(fmin)
    fmax = int(fmax)
    
    if fmin < 30 or fmax > 3900 or fmin >= fmax:
        explain.config(text = "Please specify minimum and maximum frequencies in the range 30 - 3900, in the order minimum to maximum, with the specified minimum smaller than the maximum.")
        run["state"] = 'normal'
        return 0
    
    explain.config(text = "Processing. Please be patient - the music of many generations takes time.")
    
    lastgens = sonify_general(rs, gen0, ngs, ns, rmode, fmin, fmax) # make the music!
    
    if 1 < ngs < 10:
        explain.config(text = 'Success! Generations sonified:' + '\n' + lastgens + '\n' + "You should find " + str(ns) + " midi files saved in the directory where this program was run.")
    elif ngs == 1:
        explain.config(text = 'Success! Generations sonified:' + '\n' + lastgens + '\n' + "You should find " + str(ns) + " midi file saved in the directory where this program was run.")
    else:
        explain.config(text = 'Success! You have sonified too many generations to display, but you should find ' + str(ns) + " midi files saved in the directory where this program was run.")
        
    run["state"] = 'normal' # allow running again


# In[23]:


# Make the GUI

root = Tk()
root.title("Sonify automata!")
root.geometry("900x650")
root.resizable(False, False) # expanding window will shift widgets
s = Style()
s.theme_use('clam')

w = Message(root, text="""This is an interface for the production of algorithmic music using elementary cellular automata. Such an automaton is one-dimensional, composed of a series of cells that can be on or off - alive or dead. Such a sequence can be modeled particularly well using bits, which take the values 1 for alive and 0 for dead. Thus the state of a cellular automaton at any time can be expressed as a number in binary. 
            
            The automaton can take many different values over time, where the passage of time is a progression of generations. Each generation is constructed from the previous one with respect to a ruleset. This ruleset is also a binary number, which converted to base 10 is referred to as Wolfram code, after the physicist Stephen Wolfram. 
            
            Consider a first generation of 0111, and a ruleset of 01001000 (every ruleset is 8-bit). Each bit in the current generation has a 'neighborhood' together with the bit immediately to its right and the bit to its immediate left. For example, the second bit from the right in our first generation has neighborhood 111, which corresponds to the decimal number 7. The seventh bit in the ruleset is 1. Thus in the next generation, the second bit from the right will be 1. To ensure that the edge bits have a neighborhood of three, the generation is padded with zeros; the first one, for example, becomes 001110. 
            
            To use this tool, you must specify a ruleset and a first generation. Write both in base 10. You must also decide how many generations of the automaton you will sonify, as well as how many generations at a time you want to listen to. This number of generations is the number of streams to which notes corresponding to 0 and 1-valued bits will be appended. To listen to four generations at once for a total number of 16 generations, for example, will produce music with a quarter of the duration of the music resulting from one generation at a time, appended to a single stream. 
            
            You must also choose what notes to assign to your 0's and 1's. For the 0's there are two options: the 1-frequency at a lower volume, or a rest. For the 1's, the frequency is dependent on the generation, and will be spaced linearly across generations. Enter minimum and maximum frequencies for your first and last generations, and the frequencies for the generations in between will steadily increase to the maximum.""")

w.config(padx = 50, pady = 20, justify = LEFT, width = 700)
w.pack(side = TOP)

# will be arguments to sonify_general

ruleset = StringVar()
gen = StringVar()
nstreams = StringVar()
ngens = StringVar()
fmaxmin = StringVar()

choice = IntVar() # for info
mode = IntVar() # for 0-bit mode

entries = ["Ruleset:", "Generation 0:", "Number of streams:", "Number of generations:", "Minimum & maximum frequency:"]
textvars = [ruleset, gen, nstreams, ngens, fmaxmin]

# for inputs

for i, entry in enumerate(entries):
    Label(root, text = entry).place(x = 100, y = 420 + 25 * i)

for i, textvar in enumerate(textvars):
    Entry(root, textvariable = textvar).place(x = 300, y = 420 + 25 * i)
    
# for 0-bit mode

Label(root, text = "Mode for 0-bits:").place(x = 100, y = 545)
rest = Radiobutton(root, text = "Rest", var = mode, value = 0, command = mode_inf).place(x = 300, y = 545)
low = Radiobutton(root, text = "Low", var = mode, value = 1, command = mode_inf). place(x = 350, y = 545)

# if user wants to understand their options better

for i in range(5):
    Radiobutton(root, text = "More info", var = choice, value = i, command = info).place(x = 450, y = 420 + i * 25)

# text output to inform user
    
explain = Label(root, text = "If you click to learn more about any of the inputs, it will display here.", background = 'white', wraplength = 250, padding = 10)
explain.place(x = 550, y = 410)

run = Button(root, text = "Run!", command = activate)
run.place(x = 445, y = 560)

root.mainloop()


# In[ ]:




