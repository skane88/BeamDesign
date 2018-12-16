'''
Provides a type that contains information on the symmetry properties
of a section.

Doing this rather than using strings or integers etc. ensures that the exact
value that specifies a type of symmetry can be guaranteed through an equality
test such as str(testval) == str(Symmetry(['x', 'y'])), to minimise reliance
on hard-coded strings or integers e.g. testval = 'Point'.
'''

class Symmetry(object):
    '''
    This class provides a 'Type' that can be used to identify
    sections as symmetric or not.
    
    Properties / methods are:
    
    symmetry: returns a string describing the symmetry.
    axes: a list containing the axes of symmetry.
    symcount: the number of axes of symmetry.
    '''

    def __init__(self, axes = []):
        '''
        Creates a symmetry object.

        axes: a list containing 'x', 'y', 'point' or a list of axes as
            float / interger angle values (radians).
        '''
        self._axes = axes

    def __str__(self):
        return self.symmetry

    def __repr__(self):
        return "Symmetry(" + repr(self.axes) + ")"


    @property
    def symmetry(self):
        '''
        Returns a string describing the symmetry of the object.
        This string is based on the self.axes property.

        Currently valid returns are:
        
        Double: doubly symmetric section. axes list contains
            ['x', 'y']
        Single: singly symmetric section. axes list contains
            ['x'], ['y'] or a single value.
        Point: point symmetric section. axes list contains
            ['point']
        None: no symmetry or not defined. axes list is empty
            or contains more than 2x axes.
        '''

        if len(self.axes)==0:
            return "None"
        elif len(self.axes)==2 and 'x' in self.axes and 'y' in self.axes:
            return 'Double'
        elif len(self.axes)==1 and (self.axes[0] == 'point' or
                                    self.axes[0] == "Point" or
                                    self.axes[0] == 'POINT'):
            return 'Point'
        elif len(self.axes) ==1:
            return 'Single'
        else:
            return "None"

    @property
    def axes(self):
        '''
        axes stores a list of the symmetry axes of the shape.

        This should be a list with either:
        "x", "y", "point" or float /integer values of the angles of axes of
            symmmetry (in radians).
        '''
        return self._axes
    @axes.setter
    def axes(self, axes):

        #simply set axes to axes. The return string value at the moment
        #appears to handle all potential cases so no need to check
        #this value at the moment - result of str(self) simply defaults
        #to 'None' at the moment. This should be conservative in most cases.
        
        self._axes = axes   

    @property
    def symcount(self):
        '''
        The number of degrees of symmetry that the object has. Based on the 
        length of the self.axes list. 'Point' symmetry counts as a single
        degree of symmetry.
        '''
        return len(self.axes)