from datetime import datetime
from typing import Optional, List, Tuple

from django import forms
from django.db import transaction
import astropy.units as u

from bhtom2.brokers.bhtom_broker import BHTOMBroker, LightcurveUpdateReport, return_for_no_new_points
from bhtom2.external_service.data_source_information import DataSource, TARGET_NAME_KEYS
from bhtom_base.bhtom_alerts.alerts import GenericQueryForm
from bhtom_base.bhtom_dataproducts.models import DatumValue
from bhtom_base.bhtom_dataproducts.models import ReducedDatum


class NewBrokerQueryForm(GenericQueryForm):
    target_name = forms.CharField(required=False)

    def clean(self):
        super().clean()


class NewBroker(BHTOMBroker):
    name = ''  # Add the DataSource.XXX.name here -- DataSource is an enum with all possible sources of data
    # bhtom2.external_service.data_source_information

    form = NewBrokerQueryForm

    def __init__(self):
        super().__init__(DataSource.XXX)  # Add the DataSource here

        # If the survey is e.g. a space survey, fill the facility and observer names in and treat is as a constant
        self.__FACILITY_NAME: str = ""
        self.__OBSERVER_NAME: str = ""

        self.__target_name_key: str = TARGET_NAME_KEYS.get(self.__data_source, self.__data_source.name)

        # If the data should be checked from time to time (for alerts), assing the self.__update_cadence
        # If the data should be fetched just once, leave None
        # Remember to pass it in astropy.unit format, e.g. 6*u.h for 6 hours
        self.__update_cadence = None

        # If you are going to perform searches by coordinates, you might want to change the max_separation
        # Remember to pass it in astropy.unit format as well
        # Here: 5 arcseconds
        self.__cross_match_max_separation = 5*u.arcsec

    def fetch_alerts(self, parameters):
        pass

    def fetch_alert(self, target_name):
        pass

    def to_generic_alert(self, alert):
        pass

    def process_reduced_data(self, target, alert=None) -> Optional[LightcurveUpdateReport]:
        # There are two options of querying: either by name or coordinates. This depends on the survey.
        # For the coordinates, a BHTOMBroker value is introduced: self.cross_match_separation
        survey_name: Optional[str] = self.get_target_name(target)

        if not survey_name:
            # Change the error message
            self.logger.debug(f'No <Survey> name for {target.name}')
            return return_for_no_new_points()

        # Change the log message
        self.logger.debug(f'Updating <Survey> lightcurve for {survey_name}, target: {target.name}')

        # We are going to probably obtain some response from an API call or using a python package
        response: str = ''

        # Process the data here to obtain a numpy array, list, or whatever feels comfortable to process
        data: List[Tuple[datetime, DatumValue]] = []

        # Leave the try/except so that any erronerous data doesn't cause anything to break

        try:
            # Change the fields accordingly to the data format
            # Data could be a dict or pandas table as well
            reduced_datums = [ReducedDatum(target=target,
                                           data_type='photometry',
                                           timestamp=datum[0],
                                           mjd=datum[1].mjd,
                                           value=datum[1].value,
                                           source_name=self.name,
                                           source_location='',  # e.g. alerts url
                                           error=datum[1].error,
                                           filter=datum[1].filter,
                                           observer=self.__OBSERVER_NAME,
                                           facility=self.__FACILITY_NAME)
                              for datum in data]  # Inline loop
            with transaction.atomic():
                new_points = len(ReducedDatum.objects.bulk_create(reduced_datums, ignore_conflicts=True))
        except Exception as e:
            self.logger.error(f'Error while saving reduced datapoints for {target.name}: {e}')
            return return_for_no_new_points()

        return LightcurveUpdateReport(new_points=new_points)
