# coding=UTF-8
# Author: Dennis Lutter <lad1337@gmail.com>

# URL: https://sickchill.github.io
#
# This file is part of SickChill.
#
# SickChill is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickChill is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickChill. If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=line-too-long

"""
Create a test database for testing.

Methods:
    create_test_log_folder
    create_test_cache_folder
    setup_test_db
    teardown_test_db
    setup_test_episode_file
    teardown_test_episode_file
    setup_test_show_dir
    teardown_test_show_dir

Classes:
    SickChillTestDBCase
    TestDBConnection
    TestCacheDBConnection
"""

from __future__ import print_function, unicode_literals

import os.path
import shutil
import sys
import unittest

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configobj import ConfigObj
from sickchill import db, providers
from sickchill.databases import cache_db, failed_db, mainDB
from sickchill.providers.nzb.newznab import NewznabProvider
from sickchill.tv import TVEpisode, TVShow
import sickchill

# pylint: disable=import-error


# =================
#  test globals
# =================
TEST_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DB_NAME = "sickbeard.db"
TEST_CACHE_DB_NAME = "cache.db"
TEST_FAILED_DB_NAME = "failed.db"

SHOW_NAME = "show name"
SEASON = 4
EPISODE = 2
FILENAME = "show name - s0" + str(SEASON) + "e0" + str(EPISODE) + ".mkv"
FILE_DIR = os.path.join(TEST_DIR, SHOW_NAME)
FILE_PATH = os.path.join(FILE_DIR, FILENAME)
SHOW_DIR = os.path.join(TEST_DIR, SHOW_NAME + " final")
PROCESSING_DIR = os.path.join(TEST_DIR, 'Downloads')
NUM_SEASONS = 5
EPISODES_PER_SEASON = 20

# =================
#  prepare env functions
# =================
def create_test_log_folder():
    """
    Create a log folder for test logs.
    """
    if not os.path.isdir(sickchill.LOG_DIR):
        os.mkdir(sickchill.LOG_DIR)


def create_test_cache_folder():
    """
    Create a cache folder for caching tests.
    """
    if not os.path.isdir(sickchill.CACHE_DIR):
        os.mkdir(sickchill.CACHE_DIR)

# call env functions at appropriate time during SickChill var setup

# =================
#  SickChill globals
# =================
sickchill.SYS_ENCODING = 'UTF-8'

sickchill.showList = []
sickchill.QUALITY_DEFAULT = 4  # hdtv
sickchill.SEASON_FOLDERS_DEFAULT = 0

sickchill.NAMING_PATTERN = ''
sickchill.NAMING_ABD_PATTERN = ''
sickchill.NAMING_SPORTS_PATTERN = ''
sickchill.NAMING_MULTI_EP = 1

sickchill.TV_DOWNLOAD_DIR = PROCESSING_DIR

sickchill.PROVIDER_ORDER = ["sick_beard_index"]
sickchill.newznabProviderList = NewznabProvider.providers_list("'Sick Beard Index|http://lolo.sickchill.com/|0|5030,5040|0|eponly|0|0|0!!!NZBs.org|https://nzbs.org/||5030,5040,5060,5070,5090|0|eponly|0|0|0!!!Usenet-Crawler|https://usenet-crawler.com/||5030,5040,5060|0|eponly|0|0|0'")
sickchill.providerList = providers.makeProviderList()

sickchill.PROG_DIR = os.path.abspath(os.path.join(TEST_DIR, '..'))
sickchill.DATA_DIR = TEST_DIR
sickchill.CONFIG_FILE = os.path.join(sickchill.DATA_DIR, "config.ini")
sickchill.CFG = ConfigObj(sickchill.CONFIG_FILE, encoding='UTF-8')
sickchill.GUI_NAME = 'slick'

sickchill.BRANCH = sickchill.config.check_setting_str(sickchill.CFG, 'General', 'branch')
sickchill.CUR_COMMIT_HASH = sickchill.config.check_setting_str(sickchill.CFG, 'General', 'cur_commit_hash')
sickchill.GIT_USERNAME = sickchill.config.check_setting_str(sickchill.CFG, 'General', 'git_username')
sickchill.GIT_PASSWORD = sickchill.config.check_setting_str(sickchill.CFG, 'General', 'git_password', censor_log=True)

sickchill.LOG_DIR = os.path.join(TEST_DIR, 'Logs')
sickchill.logger.log_file = os.path.join(sickchill.LOG_DIR, 'test_sickchill.log')
create_test_log_folder()

sickchill.CACHE_DIR = os.path.join(TEST_DIR, 'cache')
create_test_cache_folder()

# pylint: disable=no-member
sickchill.logger.init_logging(False, True)


# =================
#  dummy functions
# =================
def _dummy_save_config():
    """
    Override the SickChill save_config which gets called during a db upgrade.

    :return: True
    """
    return True

# this overrides the SickChill save_config which gets called during a db upgrade
# this might be considered a hack
mainDB.sickchill.save_config = _dummy_save_config


def _fake_specify_ep(self, season, episode):
    """
    Override contact to TVDB indexer.

    :param self: ...not used
    :param season: Season to search for  ...not used
    :param episode: Episode to search for  ...not used
    """
    _ = self, season, episode  # throw away unused variables


# the real one tries to contact TVDB just stop it from getting more info on the ep
TVEpisode.specifyEpisode = _fake_specify_ep


# =================
#  test classes
# =================
class SickChillTestDBCase(unittest.TestCase):
    """
    Superclass for testing the database.

    Methods:
        setUp
        tearDown
    """
    def setUp(self):
        sickchill.showList = []
        setup_test_db()
        setup_test_episode_file()
        setup_test_show_dir()

    def tearDown(self):
        sickchill.showList = []
        teardown_test_db()
        teardown_test_episode_file()
        teardown_test_show_dir()


class SickChillTestPostProcessorCase(unittest.TestCase):
    """
    Superclass for testing the database.

    Methods:
        setUp
        tearDown
    """
    def setUp(self):
        sickchill.showList = []
        setup_test_db()
        setup_test_episode_file()
        setup_test_show_dir()
        setup_test_processing_dir()

        show = TVShow(1, 1, 'en')
        show.name = SHOW_NAME
        show.location = FILE_DIR

        show.episodes = {}
        for season in range(1, NUM_SEASONS):
            show.episodes[season] = {}
            for episode in range(1, EPISODES_PER_SEASON):
                if season == SEASON and episode == EPISODE:
                    episode = TVEpisode(show, season, episode, ep_file=FILE_PATH)
                else:
                    episode = TVEpisode(show, season, episode)
                show.episodes[season][episode] = episode
                episode.saveToDB()

        show.saveToDB()
        sickchill.showList = [show]

    def tearDown(self):
        sickchill.showList = []
        teardown_test_db()
        teardown_test_episode_file()
        teardown_test_show_dir()
        teardown_test_processing_dir()


class TestDBConnection(db.DBConnection, object):
    """
    Test connecting to the database.
    """

    def __init__(self, filename=TEST_DB_NAME, suffix=None, row_type=None):
        if TEST_DIR not in filename:
            filename = os.path.join(TEST_DIR, filename)
        super(TestDBConnection, self).__init__(filename=filename, suffix=suffix, row_type=row_type)


class TestCacheDBConnection(TestDBConnection, object):
    """
    Test connecting to the cache database.
    """
    def __init__(self, provider_name):
        # pylint: disable=non-parent-init-called
        db.DBConnection.__init__(self, os.path.join(TEST_DIR, TEST_CACHE_DB_NAME), row_type='dict')

        # Create the table if it's not already there
        try:
            if not self.has_table(provider_name):
                sql = "CREATE TABLE [" + provider_name + "] (name TEXT, season NUMERIC, episodes TEXT, indexerid NUMERIC, url TEXT, time NUMERIC, quality TEXT, release_group TEXT)"
                self.connection.execute(sql)
                self.connection.commit()
        # pylint: disable=broad-except
        # Catching too general exception
        except Exception as error:
            if str(error) != "table [" + provider_name + "] already exists":
                raise

            # add version column to table if missing
            if not self.has_column(provider_name, 'version'):
                self.add_column(provider_name, 'version', "NUMERIC", "-1")

        # Create the table if it's not already there
        try:
            sql = "CREATE TABLE lastUpdate (provider TEXT, time NUMERIC);"
            self.connection.execute(sql)
            self.connection.commit()
        # pylint: disable=broad-except
        # Catching too general exception
        except Exception as error:
            if str(error) != "table lastUpdate already exists":
                raise

# this will override the normal db connection
sickchill.db.DBConnection = TestDBConnection
sickchill.tvcache.CacheDBConnection = TestCacheDBConnection


# =================
#  test functions
# =================
def setup_test_db():
    """
    Set up the test databases.
    """
    # Upgrade the db to the latest version.
    # upgrading the db
    db.upgrade_database(db.DBConnection(), mainDB.InitialSchema)

    # fix up any db problems
    db.sanity_check_database(db.DBConnection(), mainDB.MainSanityCheck)

    # and for cache.db too
    db.upgrade_database(db.DBConnection('cache.db'), cache_db.InitialSchema)

    # and for failed.db too
    db.upgrade_database(db.DBConnection('failed.db'), failed_db.InitialSchema)


def teardown_test_db():
    """
    Tear down the test database.
    """
    from sickchill.db import db_cons
    for connection in db_cons:
        db_cons[connection].commit()
    #     db_cons[connection].close()
    #
    # for current_db in [ TEST_DB_NAME, TEST_CACHE_DB_NAME, TEST_FAILED_DB_NAME ]:
    #    file_name = os.path.join(TEST_DIR, current_db)
    #    if os.path.exists(file_name):
    #        try:
    #            os.remove(file_name)
    #        except Exception as e:
    #            print 'ERROR: Failed to remove ' + file_name
    #            print(exception(e))


def setup_test_episode_file():
    """
    Create a test episode directory with a test episode in it.
    """
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)

    try:
        with open(FILE_PATH, 'wb') as ep_file:
            ep_file.write("foo bar")
            ep_file.flush()
    # pylint: disable=broad-except
    # Catching too general exception
    except Exception:
        print("Unable to set up test episode")
        raise


def setup_test_processing_dir():
    if not os.path.exists(PROCESSING_DIR):
        os.makedirs(PROCESSING_DIR)

    for season in range(1, NUM_SEASONS):
        for episode in range(11, EPISODES_PER_SEASON):
            path = os.path.join(PROCESSING_DIR, '{show_name}.S0{season}E{episode}.HDTV.x264.[SickChill].mkv'.format(
                show_name=SHOW_NAME, season=season, episode=episode))
            with open(path, 'wb') as ep_file:
                ep_file.write("foo bar")
                ep_file.flush()


def teardown_test_processing_dir():
    if os.path.exists(PROCESSING_DIR):
        shutil.rmtree(PROCESSING_DIR)


def teardown_test_episode_file():
    """
    Remove the test episode.
    """
    if os.path.exists(FILE_DIR):
        shutil.rmtree(FILE_DIR)


def setup_test_show_dir():
    """
    Create a test show directory.
    """
    if not os.path.exists(SHOW_DIR):
        os.makedirs(SHOW_DIR)


def teardown_test_show_dir():
    """
    Remove the test show.
    """
    if os.path.exists(SHOW_DIR):
        shutil.rmtree(SHOW_DIR)
