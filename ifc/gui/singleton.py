class Singleton(type):
    """
    This metaclass represents a Singleton object. The way it works is by using the __metaclass__ attribute
    that each class has, that is the class of a class.
    A class is always an instance of its metaclass.
    When you call a class with Class(), Python first asks the metaclass of Class, Singleton, what to do,
    allowing instance creation to be pre-empty.
    A metaclass decides what the definition of a class means and how to implement that definition.
    A singleton is special because is created only once, and a metaclass is the way you customize the
    creation of a class.
    Using a metaclass gives you more control in case you need to customize the singleton class definitions
    in other ways.
    Is better to use metaclass instead of singleton decorator because while objects created using MyClass()
    would be true singleton objects, MyClass itself is a function, not a class, so you cannot call class
    methods from it.
    To use it, from python > 3 use class MyClass(metaclass=Singleton).
    Right now when you call the constructor it doesn't initialize it every time, if you want so, use inside __call__

     else:
                cls._instances[cls].__init__(*args, **kwargs)


    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
