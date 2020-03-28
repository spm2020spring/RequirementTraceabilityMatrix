# Requirement Traceability Matrix

Requirement Traceability Matrix - Every requirement must be tested.  Trace which requirements have not been tested, and which have.

Prepare a software requirements specification file srs.txt in the following format::

    @RQ01

    This is my great requirement.



Prepare a test result file test.txt in the following format::


    @T001
    
    Test title: test case for requirement 1
    
    Test for: RQ01
    
    Description: None.
    
    Rationale: None.
    
    Input:
    
    Something.
    
    Expected output:
    
    Something else.
    
    Actual output:
    
    As expected.
    
    Diagnosis:
    
    Status: F
    
    Signature: Hui
    
    Date: 2020-03-28
    


Download RTM.py and run it using this command `python RTM.py`.

The traceability matrix is included in a newly generated by called test_report.html.
