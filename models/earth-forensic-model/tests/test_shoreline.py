import unittest

from earth_forensic_model.shoreline import (
    SeaLevelScenario,
    Site,
    calculate_exposure,
)


class ShorelineKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mis2 = SeaLevelScenario(
            scenario_id="MIS_2",
            age_ka_bp=24,
            global_mean_sea_level_m=-130.0,
            standard_deviation_m=4.38,
        )

    def test_outer_shelf_is_likely_exposed_under_eustatic_only_case(self) -> None:
        result = calculate_exposure(
            self.mis2,
            Site(
                site_id="outer_shelf",
                present_elevation_m=-100,
                elevation_standard_deviation_m=5,
            ),
        )
        self.assertGreater(result.probability_exposed, 0.95)
        self.assertEqual(result.classification, "likely_exposed")

    def test_deep_ridge_remains_likely_submerged(self) -> None:
        result = calculate_exposure(
            self.mis2,
            Site(
                site_id="deep_ridge",
                present_elevation_m=-650,
                elevation_standard_deviation_m=25,
            ),
        )
        self.assertLess(result.probability_exposed, 0.05)
        self.assertEqual(result.classification, "likely_submerged")

    def test_positive_local_rsl_anomaly_can_reverse_eustatic_result(self) -> None:
        eustatic_only = calculate_exposure(
            self.mis2,
            Site(
                site_id="shelf",
                present_elevation_m=-100,
                elevation_standard_deviation_m=5,
            ),
        )
        near_field = calculate_exposure(
            self.mis2,
            Site(
                site_id="shelf",
                present_elevation_m=-100,
                elevation_standard_deviation_m=5,
                local_rsl_anomaly_m=50,
                local_rsl_standard_deviation_m=20,
            ),
        )
        self.assertGreater(eustatic_only.probability_exposed, 0.95)
        self.assertLess(near_field.probability_exposed, 0.95)
        self.assertEqual(near_field.classification, "indeterminate")

    def test_negative_uncertainty_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Site(
                site_id="bad",
                present_elevation_m=0,
                elevation_standard_deviation_m=-1,
            )


if __name__ == "__main__":
    unittest.main()
