# --------------------------------------------------
# Building Energy Baseline Analysis Package
#
# Copyright (c) 2013, The Regents of the University of California, Department
# of Energy contract-operators of the Lawrence Berkeley National Laboratory.
# All rights reserved.
# 
# The Regents of the University of California, through Lawrence Berkeley National
# Laboratory (subject to receipt of any required approvals from the U.S.
# Department of Energy). All rights reserved.
# 
# If you have questions about your rights to use or distribute this software,
# please contact Berkeley Lab's Technology Transfer Department at TTD@lbl.gov
# referring to "Building Energy Baseline Analysis Package (LBNL Ref 2014-011)".
# 
# NOTICE: This software was produced by The Regents of the University of
# California under Contract No. DE-AC02-05CH11231 with the Department of Energy.
# For 5 years from November 1, 2012, the Government is granted for itself and
# others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide
# license in this data to reproduce, prepare derivative works, and perform
# publicly and display publicly, by or on behalf of the Government. There is
# provision for the possible extension of the term of this license. Subsequent to
# that period or any extension granted, the Government is granted for itself and
# others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide
# license in this data to reproduce, prepare derivative works, distribute copies
# to the public, perform publicly and display publicly, and to permit others to
# do so. The specific term of the license can be identified by inquiry made to
# Lawrence Berkeley National Laboratory or DOE. Neither the United States nor the
# United States Department of Energy, nor any of their employees, makes any
# warranty, express or implied, or assumes any legal liability or responsibility
# for the accuracy, completeness, or usefulness of any data, apparatus, product,
# or process disclosed, or represents that its use would not infringe privately
# owned rights.
# --------------------------------------------------

import unittest

from os import path
from loadshape import Loadshape, Series, Tariff

class TestLoadshape(unittest.TestCase):

    def get_kw_data_filepath(self):
        test_dir = path.dirname(path.abspath(__file__))
        return path.join(test_dir, 'data', 'test_kw_small.csv')

    def get_temp_data_filepath(self):
        test_dir = path.dirname(path.abspath(__file__))
        return path.join(test_dir, 'data', 'test_temp_small.csv')

    def get_test_tariff(self):
        test_dir = path.dirname(path.abspath(__file__))
        return path.join(test_dir, 'data', 'test_tariff.json')
    
    def test_baseline_without_temp(self):
        b = Loadshape(self.get_kw_data_filepath(),
                     timezone='America/Los_Angeles',
                     log_level=30)
        prediction = b.baseline()
        assert len(prediction.data()) > 0
    
    def test_baseline_with_temp(self):
        b = Loadshape(self.get_kw_data_filepath(),
                     self.get_temp_data_filepath(),
                     timezone='America/Los_Angeles',
                     log_level=30)
        prediction = b.baseline()
        assert len(prediction.data()) > 0
    
    def test_diff(self):
        from loadshape.utils import get_timezone
        l_data   = [(1379487600, 5.0), (1379488500, 5.0), (1379489400, 5.0), (1379490300, 5.0), (1379491200, 5.0)]
        b_data   = [(1379487600, 4.0), (1379488500, 4.0), (1379489400, 4.0), (1379490300, 4.0), (1379491200, 4.0)]
        
        expected_kw_diff                = [(1379488500, 1), (1379489400, 1), (1379490300, 1), (1379491200, 1)]
        expected_cumulative_kwh_diff    = [(1379487600, 0), (1379488500, 0.25), (1379489400, 0.5), (1379490300, 0.75), (1379491200, 1.0)]
        expected_cumulative_kwh_base    = [(1379487600, 0), (1379488500, 1.0), (1379489400, 2.0), (1379490300, 3.0), (1379491200, 4.0)]

        b = Loadshape(l_data, timezone='America/Los_Angeles', log_level=30)
        b.baseline_series = Series(b_data, get_timezone('America/Los_Angeles'))
        
        kw_diff, kw_base, cumulative_kwh_diff, cumulative_kwh_base = b.diff()

        assert kw_diff.data() == expected_kw_diff
        assert cumulative_kwh_diff.data() == expected_cumulative_kwh_diff
        assert kw_base.data() == b_data[1:]
        assert cumulative_kwh_base.data() == expected_cumulative_kwh_base

    def test_cost(self):
        l_data      = [(1379487600, 5.0), (1379488500, 5.0), (1379489400, 5.0), (1379490300, 5.0), (1379491200, 5.0)]
        cost        = [(1379487600, 0.0), (1379488500, 0.17), (1379489400, 0.17), (1379490300, 0.17), (1379491200, 0.17)]
        cumulative_cost = [(1379487600, 0.0), (1379488500, 0.17), (1379489400, 0.34), (1379490300, 0.52), (1379491200, 0.69)]

        tariff = Tariff(tariff_file=self.get_test_tariff(), timezone='America/Los_Angeles')
        ls = Loadshape(l_data, timezone='America/Los_Angeles', log_level=30, tariff=tariff)
        cost_out, cumulative_cost_out = ls.cost()

        assert cost_out.data() == cost
        assert cumulative_cost_out.data() == cumulative_cost

    def test_one_step_output_time_series_generator(self):
        start_at = 1379487600
        end_at = 1379488500
        l = Loadshape([], log_level=40, timezone='America/Los_Angeles')
        s = l._build_output_time_series(start_at, end_at, step_count=1)
        assert len(s.data()) == 2
        assert s.start_at() == start_at
        assert s.end_at() == end_at

    def test_many_step_output_time_series_generator(self):
        start_at = 1379487600
        end_at = start_at + (900 * 5)
        l = Loadshape([], log_level=40, timezone='America/Los_Angeles')
        s = l._build_output_time_series(start_at, end_at, step_size=900)
        assert len(s.data()) == 6
        assert s.start_at() == start_at
        assert s.end_at() == end_at

def main():
    unittest.main()

if __name__ == '__main__':
    main()
