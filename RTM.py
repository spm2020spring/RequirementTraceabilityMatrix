# Purpose: trace which requirements have not been tested.
#
# Usage: python RTM.py
#
# Prerequisites: prepare srs.txt (software requirements specification file) and test.txt (test result file).
# Output is a HTML report named test_report.html.
#
# srs.txt format:
#
#    @RQ01
#  
#    This is my great requirment.
#
#
# test.txt format:
#
#    @T001
#    
#    Test title: test case for requirement 1
#    
#    Test for: RQ01
#    
#    Description: None.
#    
#    Rationale: None.
#    
#    Input:
#    
#    Something.
#    
#    Expected output:
#    
#    Something else.
#    
#    Actual output:
#    
#    As expected.
#    
#    Diagnosis:
#    
#    Status: F
#    
#    Signature: Hui
#    
#    Date: 2020-03-28
#
#
# License: Apache License v2.0 https://www.apache.org/licenses/LICENSE-2.0.html
#
# Copyright (C) 2020 Hui lanhui at zjnu.edu.cn

import hashlib 
import sys, os
import re


COPYRIGHT = 'Copyright (C) 2020 Lan Laboratory [lanhui@zjnu.edu.cn]'
TEST_CASE_START_SYMBOL = '@'
RECOGNIZED_TAGS = ['Test title:', 'Test for:', 'Description:', 'Rationale:', 'Input:', 'Expected output:', 'Actual output:', 'Diagnosis:', 'Status:', 'Signature:', 'Date:']


def get_id(s):
    lst = s.split('\n')
    line = lst[0]
    if line.startswith('@') and len(line) > 1:
        return line[1:]
    else:
        h = hashlib.new('ripemd160')
        h.update(s.strip().encode('utf-8'))
        return h.hexdigest()


def strip_tag(s):
    index = s.find(':')
    if index < 0:
        return s
    else:
        return s[index+1:].strip()


def get_other_fields(s):
    lst = s.split('\n')
    d = {}

    if len(lst) < 1:
        return d
    else:
        for x in lst[1:]:
            if x != '' and not x.startswith('#'):
                flag = 0
                for t in RECOGNIZED_TAGS:
                    if x.lower().startswith(t.lower()):
                        k = t.lower()
                        d[k] = strip_tag(x) + '\n'
                        flag = 1
                        break
                if flag == 0:
                    d[k] += x + '\n'
                        
                    
    return d


def record_test_case(s, d):
    if s != '':
        test_id = get_id(s)
        if not test_id in d:
            d[test_id] = get_other_fields(s)
        else:
            reallybad('Test identifiers identical in test cases: %s.' % (test_id))
        return test_id
    return None


def read_all_test_cases(fname):
    d = {}
    test_lst = []

    if not os.path.exists(fname):
        reallybad('I could not find %s.  You must provide a test result file.' % (fname))

    f = open(fname, encoding='utf8')
    lines = f.readlines()
    f.close()

    
    test = ''
    for line in lines:
        line = line.strip()
        if line.startswith('@'):
            test_id = record_test_case(test.strip(), d)
            if test_id != None:
                test_lst.append(test_id)
            test = line + '\n'
        else:
            test += line + '\n'

    if test != '':
        test_id = record_test_case(test.strip(), d)
        if test_id != None:
            test_lst.append(test_id)

    return test_lst, d


def reallybad(s):
    print(s)
    sys.exit()


def read_all_requirements(fname):
    d = {}

    if not os.path.exists(fname):
        reallybad('I could not find %s.  You must provide a requirements specification file.' % (fname))
        
    f = open(fname, encoding='utf8')
    lines = f.readlines()
    f.close()
    rq_lst = []

    k = '?a.really.strange.key.that.should.NEVER.appear!'
    for line in lines:
        line = line.strip()
        if line.startswith('@'):
            if len(line) > 1:
                k = line[1:]
                rq_lst.append(k)
                if not k in d:
                    d[k] = ''
                else:
                    reallybad('Duplicated requirement ID %s.' % (k))
        elif k in d:
            d[k] += line + '\n'

    return rq_lst, d
        


def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))


def isfail(s):
    return s.strip().upper().startswith('F')

def standard_status(s):
    s = s.strip().upper()
    if s.startswith('F'):
        return 'FAILED'
    if s.startswith('P'):
        return 'PASSED'
    return s


def make_html_string_for_string(s):
    s = s.strip()
    result = ''
    for line in s.split('\n'):
        result += '%s<br/>' % (line)
    return result


def make_html_string_for_dictionary(d):
    result = '<table>\n'
    for k in RECOGNIZED_TAGS:
        key = k.lower()
        result += '<tr>\n'
        result += '<td>%s</td><td>%s</td>\n' % (k.title(), make_html_string_for_string(d[key]))
        result += '</tr>\n'        
    result += '</table>\n'
    return result

def make_plain_string_for_dictionary(d):
    result = ''
    for k in RECOGNIZED_TAGS:
        key = k.lower()
        content = d[key]
        content = content.replace('"', '[QUOTE]')
        content = content.replace('\'', '[QUOTE]')        
        result += '%s %s\n' % (k.title(), content)
    return result

def shorten(k):
    len_limit = 6
    if len(k) > len_limit:
        return k[:len_limit]
    return k


def check_requirement_id(id_lst, valid_id_lst):
    for x in id_lst:
        if not x in valid_id_lst:
            reallybad('Identifier %s not in %s.' % (x, ','.join(valid_id_lst)))


def get_first_non_blank_line(s):
    lst = s.split('\n')
    for line in lst:
        line = line.strip()
        if line != '':
            return line
    return 'Warning: completely blank line.'

def generate_matrix(rq_lst, rq_dict, test_lst, test_dict):

    requirement_id_lst = rq_lst

    s = '''
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8"> 
    <meta charset="utf-8">
    <style>
      * {font-family: sans-serif !important;}

      :target {
	  background-color: #ffa;
      }
    </style>
    </head>
    <body>
    '''
    
    s += '<h2 id="matrix">Requirement Traceability Matrix</h2>\n'
    s += '<table border=1>\n'
    s += '<tr><td>REQUIREMENT\TEST</td>'
    for k in test_dict:
        s += '<td><a href="#%s" title="%s">%s</a></td>' % (k, k, shorten(k))
    s += '</tr>\n'
    
    for r in requirement_id_lst:
        s += '<tr>'
        s += '<td><a href="#%s" title="%s">%s</a></td>\n' % (r, get_first_non_blank_line(rq_dict[r]), r)
        count = 0
        for k in test_lst:
            if r in test_dict[k]['test for:'].strip().split(', '):
                count += 1
        for k in test_lst:
            rq_lst_in_this_test = test_dict[k]['test for:'].strip().split(', ')
            check_requirement_id(rq_lst_in_this_test, requirement_id_lst)
            if r in rq_lst_in_this_test:
                status_string = standard_status(test_dict[k]['status:'])
                if status_string == 'FAILED':
                    status_string = '<font color="red">%s</font>' % status_string
                elif status_string == 'PASSED':
                    status_string = '<font color="green">%s</font>' % status_string                    
                s += '<td><a title="%s">%s</a></td>\n' % (make_plain_string_for_dictionary(test_dict[k]), status_string)
            else:
                if count > 0:
                    s += '<td></td>\n'
                else:
                    s += '<td bgcolor="yellow"></td>\n'
        s += '</tr>\n'
    s += '</table>\n'


    s += '<h2>Requirements</h2>\n'
    for r in requirement_id_lst:
        s += '<h3 id="%s">%s</h3>\n' % (r, r)
        s += make_html_string_for_string(rq_dict[r])
        s += '<p><a href="#matrix">Top</a></p>\n'
        
    s += '<h2>Test cases</h2>\n'
    for t in test_lst:
        s += '<h3 id="%s">%s</h3>\n' % (t, t)
        s += make_html_string_for_dictionary(test_dict[t])
        s += '<p><a href="#matrix">Top</a></p>\n'


    template = '''
<script>
    function showDiv() {
       document.getElementById('TemplateInformation').style.display = "block";
    }
</script>

<input type="button" value="Show format for srs.txt and test.txt" onclick="showDiv()" />

<div id="TemplateInformation"  style="display:none;" >

<pre>
=====================
Template for srs.txt
=====================

@RQ01

This is my great requirment.


=====================
Template for test.txt
=====================

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

</pre>
</div>

'''

    report_info =  '''
    This test report was generated by RTM.py on
       <script>
            document.write(document.lastModified);
       </script>
    '''
    s += '%s<p><i>%s</i></p><p><i>%s</i></p></body>\n</html>\n' % (template, report_info, COPYRIGHT)
    return s
    
# main

rq_lst, rq_dict = read_all_requirements('srs.txt')
test_lst, test_dict = read_all_test_cases('test.txt')

f = open('test_report.html', 'w')
f.write(generate_matrix(rq_lst, rq_dict, test_lst, test_dict))
f.close()
print('Check test_report.html ...')
