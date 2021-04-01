# class mpcurses.MPcurses

## MPcurses.__init__(...)
Class constuctor

### function
> **callable** - The target function to execute.
> 
> If you intend to use MPcurses screen capabilities then ensure the function implements logging. In general, to display data to the screen you need to add a log statement for the data item and define a corresponding category for it in the **screen_layout**. MPcurses will create a log handler that will send all log messages to a thread-safe queue, upon execution it will start a background Process to execute the function, as the messages get emitted and queued, the main process will read messages off of the queue and update the curses screen according to the categories you define in **screen_layout**.
> 
> The target function must accept two arguments; the first argument for **process_data** and the second argument for **shared_data**. 
> 
> This parameter is required.

### process_data
> **list** - A list of dictionaries. Each individual dictionary will be passed to the target **function** for the respective process being executed. Thus the data defined in the dictionary should be intended to the process executing it. This is necessary if you wish to scale the execution of the target **function** across multiple processes, where each process is responsible for executing the target function on a unique set of data. The total number of elements in the list represent the total number of processes that will be executed. 
> 
> For example, specifying a value of: `[{'name': 'one'}, {'name': 'two'}, {'name': 'three'}]`
> 
> Will result in the following:
> * A total of 3 processes will be executed
> * Process #1 will execute the target function with first argument of: `{'name': 'one'}`
> * Process #2 will execute the target function with first argument of: `{'name': 'two'}`
> * Process #3 will execute the target function with first argument of: `{'name': 'three'}`
> 
> If not specified a single process will be executed for the target **function** specified.
> 
> If the **function** returns an object then the return value will be added to the `result` key in the respective dictionary. This will happen after all processes complete, for example: `[{'name': 'one', 'result': 1}, {'name': 'two', 'result': 2}, {'name': 'three', 'result': 3}]`
> 
> Default value: **[{}]**

### shared_data
> **dict** - A dictionary of key value pairs that will be passed to the target **function** for every process being executed. Thus if you have a set of data that all processes should be know then assign that data to this parameter; all processes will receive this data.
> 
> Default value: **{}**

### processes_to_start
> **int** - The number of processes to execute simultaneously. If this number is less than the number of elements in the **process_data** list, then the remaining elements in the list will be queued for execution. As a process completes the next element will be popped from the queue and executed. This number should not be greater than the number of elements in the **process_data** list.
> 
> If no value is specified and **process_data** is provided, then this number will default to the length of the **process_data** list
> 
> Default value: len(**process_data**) if **process_data** is provided

### screen_layout
> **dict** - A dictionary describing the layout and elements of the curses screen. Refer to the [screen layout](screen_layout.md) directives for the elements that can be configured.
> 
> Default value: **{}**

### init_messages
> **list** - A list of strings, each string represents a message that MPcurses will process and update the screen upon execution. MPcurses will automatically add the start time as an init message in the form of `%m/%d/%Y %H:%M:%S`.
> 
> Default value: **[]**

### get_process_data
> **callable** - A function to call that will set the value of **process_data**. This is useful if the value of **process_data** takes some time to compute. The function must include a docstr describing the purpose of the function. Upon execution, the value of the function's docstring will be displayed in the curses screen while it is being executed.
> 
> The function must accept as a first argument a dictionary, if the function requires arguments, then specify them in **shared_data** as execution will pass this to the function. 
> 
> Note that **get_process_data** and **process_data** are mutually exclusive and cannot both be set at the same time; setting both will incur a ValueError. If setting this value then you must all set **screen_layout**.
> 
> Default value: **None**

## MPcurses.execute()
Initiate execution of the MPcurses instance.
