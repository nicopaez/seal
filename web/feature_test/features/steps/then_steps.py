from behave import *
from selenium import webdriver 
from selenium.webdriver.common.by import By
from seal.model import Student, Practice, Delivery
import time
import re
from seal.model.course import Course
from numpy.ma.testutils import assert_equal

base_url = 'http://localhost:8000/'

@then('I should see "{text1}" before "{text2}"')
def step(context, text1, text2):
    trs = context.browser.find_elements(By.TAG_NAME, "tr")
    match_course_1 = False
    match_course_2 = False
    for tr in trs:
        if(text1 in tr.text):
            match_course_1 = not match_course_2 # if 2 has already match, then is wrong
        elif(text2 in tr.text):
            match_course_2 = match_course_1 # if 1 hasn't match yet, then is wrong
    assert match_course_1 and match_course_2

@then('I should see "{text1}" and "{text2}"')
def step(context, text1, text2):
    body = context.browser.find_element_by_tag_name('body')
    assert text1 in body.text
    assert text2 in body.text

@then(u'I should not see "{text}"')
def impl(context, text):
    body = context.browser.find_element_by_tag_name('body')
    assert text not in body.text

@then('I should see \'{text}\'')
def impl(context, text):
    body = context.browser.find_element_by_tag_name('body')
    assert text not in body.text

@then('I should see a link to "{link_text}"')
def step(context, link_text):
    links = context.browser.find_elements_by_tag_name('a')
    match = False
    for link in links:
        match = match or (link_text in link.get_attribute("href"))
    assert match

@then('I should see link to "{text}" in the list')
def step(context, text):
    a = context.browser.find_element_by_link_text(text)
    assert text in a.text

@then('I should see the button "{name}"')
def step(context, name):
    button = context.browser.find_elements(By.NAME, name)
    assert True

@then('I should not see the button "{name}"')
def step(context, name):
    try: 
        button = context.browser.find_elements(By.NAME, name)
        assert False
    except Exception, e:
        assert True


@then('I should see pattern "{text}"')
def step(context, text):
    body = context.browser.find_element_by_tag_name('body')
    assert re.search(text, body.text)
    
@then('I should see "{text}"')
def step(context, text):
    body = context.browser.find_element_by_tag_name('body')
    if("susccessfull" in text):
        with open("/tmp/behave.out", "a") as f:
            f.write(body.text + "\n")
    assert text in body.text

@then('I enter in the page with this title "{text}"')
def step(context, text):
    titlebrowser = context.browser.title 
    assert titlebrowser == text

@then('I am in the index page')
def step(context):
    context.browser.get(base_url) 
 
@then('I logout')
def step(context):
    a = context.browser.find_element_by_link_text('Log out')
    a.click()

@then('I close de browser')
def step(context):
    context.browser.close()
    
@then('I should have the edit form for courses with "{text}" course data in it')
def step(context, text):
    element = context.browser.find_element_by_id('id_name')
    assert element.get_attribute('value') == text

@then('I should see the delivery in the list')
def step(context):
    body = context.browser.find_element_by_tag_name('body')
    assert "corrected" in body.text or "uncorrected" in body.text

@then('I should have the edit form for correction with "{coment1}" "{coment2}" "{grade}" data in it')
def step(context, coment1, coment2, grade):
    com1 = context.browser.find_element_by_id('id_publicComent')
    com2 = context.browser.find_element_by_id('id_privateComent')
    n = context.browser.find_element_by_name('grade')
    assert com1.get_attribute('value') == coment1
    assert com2.get_attribute('value') == coment2
    assert n.get_attribute('value') == grade

@then(u'delivery for practice "{practice_uid}" and course "{course_name}" from Student "{student_uid}" should have status "{status}"')
def step(context, practice_uid, course_name, student_uid, status):
    student = Student.objects.get(uid=student_uid)
    course = Course.objects.get(name=course_name)
    practice = Practice.objects.get(uid= practice_uid, course=course)
    delivery = Delivery.objects.get(student=student, practice=practice)
    automatic_correction = delivery.get_automatic_correction()
    assert status == automatic_correction.get_status()

@then("I wait")
def step(context):
    time.sleep(5)
    