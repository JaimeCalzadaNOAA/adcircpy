from datetime import datetime, timedelta
import os
import pathlib
import shutil
import subprocess
import tempfile

import matplotlib.pyplot as plt
import numpy as np
from psutil import cpu_count

from adcircpy.mesh.adcirc_mesh import AdcircMesh
from adcircpy.model.fort15 import Fort15
from adcircpy.model.slurm.server_config import SlurmScript
from adcircpy.model.tidal_forcing import TidalForcing
from adcircpy.model.winds.wind_forcing import WindForcing
from adcircpy.outputs.collection import OutputCollection


class AdcircRun(Fort15):

    def __init__(
            self,
            mesh,
            start_date,
            end_date,
            spinup_time=None,
            tidal_forcing=None,
            wind_forcing=None,
            waves=None,
            netcdf=True,
    ):
        self._mesh = mesh
        self._start_date = start_date
        self._end_date = end_date
        self._spinup_time = spinup_time
        self._tidal_forcing = tidal_forcing
        self._wind_forcing = wind_forcing
        self._waves = waves
        self._netcdf = netcdf

    def add_elevation_output_station(self, station_name, vertices):
        self._certify_station('elevation', station_name, vertices)
        self._elevation_stations[station_name] = vertices

    def add_velocity_output_station(self, station_name, vertices):
        self._certify_station('velocity', station_name, vertices)
        self._velocity_stations[station_name] = vertices

    def add_meteorological_output_station(self, station_name, vertices):
        self._certify_station('meteorological', station_name, vertices)
        self._meteorological_stations[station_name] = vertices

    def add_concentration_output_station(self, station_name, vertices):
        self._certify_station('concentration', station_name, vertices)
        self._concentration_stations[station_name] = vertices

    def set_elevation_stations_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis
        )
        self._container['stations']['elevation'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def set_velocity_stations_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis)
        self._container['stations']['velocity'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def set_meteorological_stations_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis)
        self._container['stations']['meteorological'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def set_concentration_stations_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis)
        self._container['stations']['concentration'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def set_elevation_surface_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis)
        self._container['surface']['elevation'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def set_velocity_surface_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis)
        self._container['surface']['velocity'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def set_meteorological_surface_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis)
        self._container['surface']['meteorological'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def set_concentration_surface_output(
            self,
            sampling_frequency,
            start=None,
            end=None,
            spinup=None,
            spinup_start=None,
            spinup_end=None,
            netcdf=True,
            harmonic_analysis=False,
    ):
        self._certify_output_request(
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis)
        self._container['surface']['concentration'].update({
            'sampling_frequency': sampling_frequency,
            'start'             : start,
            'end'               : end,
            'spinup'            : spinup,
            'spinup_start'      : spinup_start,
            'spinup_end'        : spinup_end,
            'netcdf'            : netcdf,
            'harmonic_analysis' : harmonic_analysis
        })

    def remove_elevation_output_station(self, station_name):
        self._elevation_stations.pop(station_name)

    def remove_velocity_output_station(self, station_name):
        self._velocity_stations.pop(station_name)

    def remove_meteorological_output_station(self, station_name):
        self._meteorological_stations.pop(station_name)

    def remove_concentration_output_station(self, station_name):
        self._concentration_stations.pop(station_name)

    def write(self,
              output_directory: str,
              overwrite: bool = False,
              fort14: str = 'fort.14',
              fort13: str = 'fort.13',
              fort22: str = 'fort.22',
              fort15: str = 'fort.15',
              coldstart: str = 'fort.15.coldstart',
              hotstart: str = 'fort.15.hotstart',
              slurm_config: SlurmScript = None):
        output_directory = pathlib.Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=overwrite)

        if fort14:
            path = output_directory / fort14
            self.mesh.write_fort14(path, overwrite)

        if fort13:
            if len(self.mesh.get_nodal_attribute_names()) > 0:
                self.mesh.write_fort13(
                    output_directory / fort13,
                    overwrite
                )

        # when wind forcing is present, one has to divide the run
        # (almost) necessarily in two phases
        if self.spinup_time.total_seconds() == 0:
            # no spiunp time given means single phase
            # easiest way is to override IHOT for the hotstart writer.
            self._IHOT = 0
            super().write('hotstart', output_directory / fort15, overwrite)
        else:
            if self.wind_forcing is not None:
                if fort22:
                    self.wind_forcing.write(output_directory / fort22, overwrite)
            if coldstart:
                super().write('coldstart', output_directory / coldstart, overwrite)
            if hotstart:
                super().write('hotstart', output_directory / hotstart, overwrite)

            if slurm_config is not None:
                slurm_config.write(output_directory / 'slurm.job')

    def import_stations(self, fort15):
        station_types = ['NOUTE', 'NOUTV', 'NOUTM', 'NOUTC']
        for station_type in station_types:
            stations = Fort15.parse_stations(fort15, station_type)
            for name, vertices in stations.items():
                if station_type == 'NOUTE':
                    self.add_elevation_output_station(name, vertices)
                if station_type == 'NOUTV':
                    self.add_velocity_output_station(name, vertices)
                if station_type == 'NOUTM':
                    self.add_meteorological_output_station(name, vertices)
                if station_type == 'NOUTC':
                    self.add_concentration_output_station(name, vertices)

    def run(
            self,
            outdir=None,
            nproc=-1,
            overwrite=False,
            coldstart=True,
            hotstart=True,
            server_config=None,
    ):

        if outdir is None:
            self._outdir_tmpdir = tempfile.TemporaryDirectory()
            outdir = pathlib.Path(self._outdir_tmpdir.name)
        else:
            outdir = pathlib.Path(outdir)
        #     if outdir.exists() and not overwrite:
        #         msg = f"{outdir} exists and overwrite is not enabled."
        #         raise IOError(msg)

        # if not outdir.exists():
        #     outdir.mkdir(parents=True)

        # local adcirc run

        if server_config is None:
            self._run_local(
                nproc=nproc,
                outdir=outdir,
                overwrite=overwrite,
                coldstart=coldstart,
                hotstart=hotstart
            )

            # server adcirc run
        else:
            server_config.run(
                driver=self,
                outdir=outdir,
                overwrite=overwrite,
                coldstart=coldstart,
                hotstart=hotstart
            )

        self._load_outdir(outdir)

        return self._output_collection

    @property
    def mesh(self):
        return self._mesh

    @property
    def tidal_forcing(self):
        return self._tidal_forcing

    @property
    def wind_forcing(self):
        return self._wind_forcing

    @property
    def waves(self):
        return self._waves

    @property
    def spinup_time(self):
        return self._spinup_time

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def forcing_start_date(self):
        return self.start_date - self.spinup_time

    @property
    def spinup_factor(self):
        try:
            return self.__spinup_factor
        except AttributeError:
            return 1.

    @property
    def coldstart(self):
        return self.fort15('coldstart')

    @property
    def hotstart(self):
        return self.fort15('hotstart')

    @property
    def netcdf(self):
        return self._netcdf

    @property
    def container(self):
        return self._container.copy()

    @property
    def stations_output(self):
        return self.container['stations']

    @property
    def elevation_stations_output(self):
        return self.stations_output['elevation']

    @property
    def velocity_stations_output(self):
        return self.stations_output['velocity']

    @property
    def meteorological_stations_output(self):
        return self.stations_output['meteorological']

    @property
    def concentration_stations_output(self):
        return self.stations_output['concentration']

    @property
    def elevation_stations(self):
        return self.elevation_stations_output['collection']

    @property
    def velocity_stations(self):
        return self.velocity_stations_output['collection']

    @property
    def meteorological_stations(self):
        return self.meteorological_stations_output['collection']

    @property
    def concentration_stations(self):
        return self.concentration_stations_output['collection']

    @property
    def surface_outputs(self):
        return self.container['surface']

    @property
    def elevation_surface_output(self):
        return self.surface_outputs['elevation']

    @property
    def velocity_surface_output(self):
        return self.surface_outputs['velocity']

    @property
    def meteorological_surface_output(self):
        return self.surface_outputs['meteorological']

    @property
    def concentration_surface_output(self):
        return self.surface_outputs['concentration']

    @property
    def output_collection(self):
        return self._output_collection

    def _load_outdir(self, outdir):

        # gather outputs
        maxele = pathlib.Path(outdir / 'hotstart/maxele.63.nc')

        self._output_collection = OutputCollection(
            maxele=maxele if maxele.is_file() else None,
            crs=self.mesh.crs
        )

        if len(self._output_collection) == 0:
            raise Exception('No outputs found.')

        # for output in self._output_collection:
        #     output.make_plot(show=True)

        return self.output_collection

    def _run_padcirc(self, rundir, nproc=-1):
        nproc = self._get_nproc(nproc)
        cmd = list()
        cmd.append('mpiexec')
        cmd.append('-n')
        cmd.append(str(nproc))
        cmd.append('padcirc')
        err = self._launch_command(cmd, rundir)

        msg = "** ERROR: Elevation.gt.ErrorElev, ADCIRC stopping. **"
        if msg in "".join(err):
            print(msg)
            self._handle_blowup(err)

        # filter IEEE_UNDERFLOW_FLAG IEEE_DENORMAL
        msg = "Note: The following floating-point exceptions are signalling:"
        err = [line for line in err if msg not in line]
        if len(err) > 0:
            if msg not in "".join(err):
                msg = "\n"
                msg += "".join(err)
                raise Exception(msg)
            else:
                raise Exception(msg)

        return err

    def _run_local(self, nproc, outdir, overwrite, coldstart, hotstart):
        self.write(outdir, overwrite)
        if self.spinup_time.total_seconds() != 0:
            if coldstart:
                self._run_coldstart(nproc, outdir)
            if hotstart:
                self._run_hotstart(nproc, outdir)
        else:
            self._run_single(nproc, outdir)

    def _run_coldstart(self, nproc, wdir):
        self._stage_files('coldstart', nproc, wdir)
        self._run_adcprep('coldstart', nproc, wdir)
        self._run_padcirc(wdir / 'coldstart', nproc)

    def _run_hotstart(self, nproc, wdir):
        self._stage_files('hotstart', nproc, wdir)
        self._run_adcprep('hotstart', nproc, wdir)
        if self.waves:
            if self.waves.model.lower() == 'swan':
                self._run_padcswan(wdir / 'hotstart', nproc)
            else:
                msg = "Unknown wave coupling type."
                raise NotImplementedError(msg)
        else:
            self._run_padcirc(wdir / 'hotstart', nproc)

    def _run_single(self, nproc, wdir):
        self._run_adcprep('./', nproc, wdir)
        self._run_padcirc(wdir, nproc)

    def _stage_files(self, runtype, nproc, wdir):

        # create run directory
        cwdir = wdir / runtype
        if cwdir.exists():
            shutil.rmtree(cwdir.absolute())
        cwdir.mkdir()

        # symlink files
        os.symlink(wdir / 'fort.14', cwdir / 'fort.14')
        os.symlink(wdir / 'fort.13', cwdir / 'fort.13')
        os.symlink(wdir / f'fort.15.{runtype}', cwdir / 'fort.15')
        if runtype == 'hotstart':
            os.symlink(wdir / f'coldstart/fort.67.nc', cwdir / 'fort.67.nc')

    def _run_adcprep(self, runtype, nproc, wdir):

        # run directory
        cwdir = wdir / runtype
        nproc = self._get_nproc(nproc)

        if nproc > 1:
            cmd = list()
            cmd.append('adcprep')
            cmd.append('--np')
            cmd.append(f"{nproc:d}")
            self._launch_command(cmd + ['--partmesh'], cwdir)
            self._launch_command(cmd + ['--prepall'], cwdir)

        else:
            raise NotImplementedError('run serial')

    def _certify_station(self, physical_var, station_name, vertices):
        keys = list(self._container['stations'][physical_var].keys())
        vertices = np.asarray(vertices)
        msg = "vertices argument must be a two-tuple of floats."
        assert vertices.shape == (2,), msg
        msg = f"station_name {station_name} "
        msg += "already exists. Station names must be unique."
        msg += f"{keys}"
        assert station_name not in keys, msg
        return tuple(vertices)

    def _handle_blowup(self, err):
        data = self._get_blowup_data(err)
        idx = np.asarray(data['maxele_node']) - 1
        ax = self.mesh.make_plot()
        self.mesh.triplot(axes=ax)
        ax.scatter(
            self.mesh.x[idx],
            self.mesh.y[idx],
            s=80,
            facecolors='none',
            edgecolors='r'
        )
        ax.axis('scaled')
        plt.show()

    def _certify_output_request(
            self,
            sampling_frequency,
            start,
            end,
            spinup,
            spinup_start,
            spinup_end,
            netcdf,
            harmonic_analysis,
    ):
        self._certify_sampling_frequency(sampling_frequency)
        self._certify__OUT__('start', start)
        self._certify__OUT__('end', end)
        self._certify_spinup(spinup)
        self._certify__OUT__('spinup_start', spinup_start)
        self._certify__OUT__('spinup_end', spinup_end)
        self._certify_netcdf(netcdf)
        self._certify_harmonic_analysis(harmonic_analysis)

    @staticmethod
    def _certify_sampling_frequency(sampling_frequency):
        msg = f"Error: sampling_frequency argument must be either None, "
        msg += f"or an instance of type {timedelta}."
        if sampling_frequency is not None:
            assert isinstance(sampling_frequency, timedelta), msg
        return sampling_frequency

    @staticmethod
    def _certify_spinup(spinup):
        msg = "Error: spinup argument must be either None "
        msg += f"or an instance of type {timedelta}."
        if spinup is not None:
            assert isinstance(spinup, timedelta), msg
        return spinup

    @staticmethod
    def _certify__OUT__(name, var):
        # certifies TOUTS* and TOUTF*
        msg = f"Error: {name} argument must be either {None}, "
        msg += f"{int} or an instance of type {timedelta}."
        assert isinstance(var, (
            type(None),
            timedelta,
            int)
                          ), msg

    @staticmethod
    def _certify_netcdf(netcdf):
        # certify netcdf ouptut request
        msg = f"Error: netcdf must be of type {bool}."
        assert isinstance(netcdf, bool), msg

    @staticmethod
    def _certify_harmonic_analysis(harmonic_analysis):
        # certify harmonic_analysis
        msg = f"Error: harmonic_analysis must be of type {bool}."
        assert isinstance(harmonic_analysis, bool), msg

    @staticmethod
    def _launch_command(cmd, rundir):
        p = subprocess.Popen(
            cmd,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=rundir.absolute()
        )
        for line in p.stdout:
            if "MPI terminated with Status =" in line:
                break
            print(line, end='')
        p.wait()
        return p.stderr.readlines()

    @staticmethod
    def _get_nproc(nproc):
        return cpu_count(logical=False) if nproc == -1 else nproc

    @staticmethod
    def _get_blowup_data(err):
        s = "".join(err).split('** WARNING: Elevation.gt.WarnElev **')
        s = [_ for _ in s if 'TIME' in _]
        blowup = {
            'timestep'   : list(),
            'time'       : list(),
            'maxele'     : list(),
            'maxele_node': list(),
            'maxvel'     : list(),
            'maxvel_node': list(),
        }
        for output in s:
            blowup['timestep'].append(
                int(output.split('TIME STEP =')[1].split()[0]))
            blowup['time'].append(
                float(output.split('TIME =')[1].split()[0]))
            blowup['maxele'].append(
                float(output.split('ELMAX =')[1].split()[0]))
            blowup['maxvel'].append(
                float(output.split('SPEEDMAX =')[1].split()[0]))
            nodes = output.split('AT NODE')
            blowup['maxele_node'].append(int(nodes[1].split()[0]))
            blowup['maxvel_node'].append(int(nodes[2].split()[0]))
        return blowup

    @property
    def _mesh(self):
        return self.__mesh

    @property
    def _tidal_forcing(self):
        return self.__tidal_forcing

    @property
    def _wind_forcing(self):
        return self.__wind_forcing

    @property
    def _waves(self):
        return self.__waves

    @property
    def _spinup_time(self):
        return self.__spinup_time

    @property
    def _start_date(self):
        return self.__start_date

    @property
    def _end_date(self):
        return self.__end_date

    @property
    def _netcdf(self):
        return self.__netcdf

    @property
    def _container(self):
        try:
            return self.__container
        except AttributeError:
            pass
        # init container
        container = dict()
        # init surface outputs attributes
        schema = {
            'sampling_frequency': None,
            'start'             : None,
            'end'               : None,
            'spinup'            : None,
            'spinup_start'      : None,
            'spinup_end'        : None,
            'netcdf'            : self.netcdf,
            'harmonic_analysis' : False,
        }
        container['surface'] = dict()
        container['surface']['elevation'] = schema.copy()
        container['surface']['velocity'] = schema.copy()
        container['surface']['meteorological'] = schema.copy()
        container['surface']['concentration'] = schema.copy()
        # init stations output attributes
        container['stations'] = dict()
        container['stations']['elevation'] = schema.copy()
        container['stations']['velocity'] = schema.copy()
        container['stations']['meteorological'] = schema.copy()
        container['stations']['concentration'] = schema.copy()
        # add a 'collections' key to hold the stations.
        container['stations']['elevation'].update(
            {'collection': dict()})
        container['stations']['velocity'].update(
            {'collection': dict()})
        container['stations']['meteorological'].update(
            {'collection': dict()})
        container['stations']['concentration'].update(
            {'collection': dict()})
        self.__container = container
        return self.__container

    @property
    def _stations_output(self):
        return self._container['stations']

    @property
    def _elevation_stations_output(self):
        return self._stations_output['elevation']

    @property
    def _velocity_stations_output(self):
        return self._stations_output['velocity']

    @property
    def _meteorological_stations_output(self):
        return self._stations_output['meteorological']

    @property
    def _concentration_stations_output(self):
        return self._stations_output['concentration']

    @property
    def _elevation_stations(self):
        return self._elevation_stations_output['collection']

    @property
    def _velocity_stations(self):
        return self._velocity_stations_output['collection']

    @property
    def _meteorological_stations(self):
        return self._meteorological_stations_output['collection']

    @property
    def _concentration_stations(self):
        return self._concentration_stations_output['collection']

    @property
    def _surface_outputs(self):
        return self._container['surface']

    @property
    def _elevation_surface_output(self):
        return self._surface_outputs['elevation']

    @property
    def _velocity_surface_output(self):
        return self._surface_outputs['velocity']

    @property
    def _meteorological_surface_output(self):
        return self._surface_outputs['meteorological']

    @property
    def _concentration_surface_output(self):
        return self._surface_outputs['concentration']

    @property
    def _output_collection(self):
        return self.__output_collection

    @_mesh.setter
    def _mesh(self, mesh):
        assert isinstance(mesh, AdcircMesh)
        if mesh.crs is None:
            msg = 'Coordinate reference system must be set before setting up a'
            msg += ' model run.'
            raise RuntimeError(msg)
        self.__mesh = mesh

    @_start_date.setter
    def _start_date(self, start_date):
        assert isinstance(start_date, datetime)
        self.__start_date = start_date

    @_end_date.setter
    def _end_date(self, end_date):
        assert isinstance(end_date, datetime)
        assert end_date > self.start_date
        self.__end_date = end_date

    @_spinup_time.setter
    def _spinup_time(self, spinup_time):
        if spinup_time is None:
            spinup_time = timedelta(0)
        assert isinstance(spinup_time, timedelta)
        self.__spinup_time = spinup_time

    @_tidal_forcing.setter
    def _tidal_forcing(self, tidal_forcing):
        if tidal_forcing is not None:
            assert isinstance(tidal_forcing, TidalForcing)
            tidal_forcing.start_date = self.start_date
            tidal_forcing.end_date = self.end_date
            tidal_forcing.spinup_time = self.spinup_time
        self.__tidal_forcing = tidal_forcing

    @_wind_forcing.setter
    def _wind_forcing(self, wind_forcing):
        if wind_forcing is not None:
            assert isinstance(wind_forcing, WindForcing)
        self.__wind_forcing = wind_forcing

    @_waves.setter
    def _waves(self, waves):
        # if waves is not None:
        #     assert isinstance(waves, WindForcing)
        self.__waves = waves

    @_netcdf.setter
    def _netcdf(self, netcdf):
        assert isinstance(netcdf, bool)
        self.__netcdf = netcdf

    @_output_collection.setter
    def _output_collection(self, output_collection):
        assert isinstance(output_collection, OutputCollection)
        self.__output_collection = output_collection
