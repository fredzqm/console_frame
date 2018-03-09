# console
# Author: Xiao Xin <xin.xiao@hotmail.com>
# Date: 03-08-18

class Console:

  MISSING_INTERMEDIATE = 'Missing intermediate path handler.'
  INVALID_OPTION_CHOICE = 'Invalid option choice'
  OPTION_CONFLICT = 'Option has been taken'
  REPL_PREFIX = '-> '
  INPUT_LOCALE = '<- {}: '
  INVALID_OPTION = '!! Invalid option; please re-enter.'
  OPTION_LOCALE = '## {}) {}'
  RETURN_OPTION = '## r) return'
  QUIT_OPTION = '## q) quit'
  PATH_SPLITER = '/'
  BAR = '=============================================='
  LEAVE_MESSAGE = 'Bye'
  
  def __init__(self, tag):
    self.structure = { 
      'tag': tag,
      'data': {},
      'next': {}
    }
    self.scope_chain = []
    self.current_path_list = []
  
  def add_handler(self, tag, path, handler):
    scope = self.structure
    if 'r' in path or 'q' in path:
      raise Exception(Console.INVALID_OPTION_CHOICE)
    while len(path) > 1:
      stage = path.pop(0)
      if stage not in scope['next']:
        raise Exception(Console.MISSING_INTERMEDIATE)
      scope = scope['next'][stage]
    if path[0] in scope['next']:
      raise Exception(OPTION_CONFLICT)
    scope['next'][path[0]] = {
      'tag': tag,
      'handler': handler,
      'data': {},
      'next': {}
    }

  def path(self, tag, path):
    path = path.split(Console.PATH_SPLITER)
    def path_wrapper(handler):
      self.add_handler(tag, path, handler)
      return handler
    return path_wrapper

  def multipath(self, tag, path_list, route):
    path_list = [path.split(Console.PATH_SPLITER) for path in path_list]
    def multipath_wrapper(handler):
      for path in path_list:
        path.append(route)
        self.add_handler(tag, path, handler)
      return handler
    return multipath_wrapper

  def prompt_for_arguments(self, prompts):
    def wrapper(function):
      def call_with_request_arguements():
        argv = [raw_input(Console.INPUT_LOCALE.format(text)) for text in prompts]
        function(*argv)
      return call_with_request_arguements
    return wrapper

  def initialize(self):
    self.scope_chain = [self.structure]
    self.current_path_list = []

  def reduce_scope(self):
    if self.scope_chain: self.scope_chain.pop()
    if self.current_path_list: self.current_path_list.pop()

  def extend_scope(self, option):
    self.current_path_list.append(option)
    self.scope_chain.append(self.current_scope()['next'][option])

  def current_scope(self):
    return self.scope_chain[-1]

  def is_at_root(self):
    return self.current_scope() == self.structure

  def current_path(self):
    return Console.PATH_SPLITER.join(self.current_path_list)
  
  def save_data_to_current_scope(self, key, value):
    self.current_scope()['data'][key] = value

  def read_data_from_current_scope(self, key):
    return self.current_scope()['data'].get(key, None)

  def locate_scope_from_path(self, path):
    scope = self.structure
    for stage in path.split(Console.PATH_SPLITER):
      scope = scope['next'][stage]
    return scope

  def save_data_to_path(self, path, key, value):
    self.locate_scope_from_path(path)['data'][key] = value

  def read_data_from_path(self, path, key):
    return self.locate_scope_from_path(path)['data'].get(key, None)

  def quit(self):
    self.scope_chain = []
    self.current_path_list = []

  def run(self):
    self.initialize()
    while self.scope_chain:
      scope = self.current_scope()
      if not scope['next']: 
        self.reduce_scope()
        continue
      print scope['tag']
      print Console.BAR
      next_scope = scope['next']
      for option in next_scope:
        print Console.OPTION_LOCALE.format(option, next_scope[option]['tag'])
      if not self.is_at_root(): print Console.RETURN_OPTION
      print Console.QUIT_OPTION
      option = raw_input(Console.REPL_PREFIX)
      if option == 'r': self.reduce_scope()
      elif option == 'q': self.quit()
      elif option not in next_scope: print Console.INVALID_OPTION
      else:
        self.extend_scope(option)
        next_scope[option]['handler']()
      print
    print Console.LEAVE_MESSAGE
