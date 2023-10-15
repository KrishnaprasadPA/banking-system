**This is a gRPC banking project**

Execution steps:

1. Form a valid input file say ```input.json```
2. Execute run_branch with command : ```python3 run_branch.py input.json```
3. Execute run_customer with command : ```python3 run_customer.py input.json```
3. Outputs will be stored to ```output.json``` file
4. Terminate all servers



**Important files:**

```banking.proto``` - protocol buffer file

```banking_pb2.py``` - python module generated by protoc

```banking_pb2_grpc.py```  -  python module generated by protoc with gRPC service implementations 

```customer.py``` - client customer file

```branch.py``` - server branch file

```run_branch.py```  -  python file to read input and start branch servers

```run_customer.py``` - python file to read input file, execute customer events and store the results in the output file

```input.json``` - input file for branch and customer