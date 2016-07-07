#!/bin/env python3
#encoding:utf-8
from selenium import webdriver
from bs4 import BeautifulSoup

def get_soup(url):

    driver = webdriver.PhantomJS("./phantomjs")
    driver.set_window_size(1366, 768)
    driver.get(url)
    bodyStr= driver.find_element_by_tag_name("body").get_attribute("innerHTML")
    driver.quit()
    soup = BeautifulSoup(bodyStr, "lxml")
    return soup

print(get_soup("http://www.youdaili.net/"))