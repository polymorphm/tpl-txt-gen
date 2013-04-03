# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2012, 2013 Andrej A Antonov <polymorphm@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

import os.path, random

# in template file -- using like:
#       # -*- mode: text; coding: utf-8 -*-
#       ${custom('fignya:lib_tpl_txt_gen_2012_09_27.EXAMPLE__custom_func')('фигня111')}
#       ${custom('fignya:lib_tpl_txt_gen_2012_09_27.EXAMPLE__custom_func')('фигня222')}

def EXAMPLE__fignya_func_factory(environ_ref):
    root_dir = os.path.abspath(environ_ref().root_dir)
    r0 = random.randrange(0, 1000000)
    
    def func_factory():
        
        r1 = random.randrange(0, 1000000)
        
        def func(x):
            r2 = random.randrange(0, 1000000)
            
            return '[{!r}({!r},{!r},{!r},{!r})]'.format(x, root_dir, r0, r1, r2)
        
        return func
    
    return func_factory

FUNC_FACTORY_MAP = {
    'fignya': EXAMPLE__fignya_func_factory,
}
