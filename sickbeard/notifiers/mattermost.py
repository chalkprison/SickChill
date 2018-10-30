# coding=utf-8

# Author: Patrick Begley<forge33@gmail.com>
#        modified for mattermost by chalkprison <chalkprison@batcave.pw>
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
from __future__ import unicode_literals

import json

import requests
import six

import sickbeard
from sickbeard import common, logger
from sickchill.helper.exceptions import ex


class Notifier(object):

    MATTERMOST_WEBHOOK_URL = ''

    def notify_snatch(self, ep_name):
        if sickbeard.MATTERMOST_NOTIFY_SNATCH:
            self._notify_MATTERMOST(common.notifyStrings[common.NOTIFY_SNATCH] + ': ' + ep_name)

    def notify_download(self, ep_name):
        if sickbeard.MATTERMOST_NOTIFY_DOWNLOAD:
            self._notify_MATTERMOST(common.notifyStrings[common.NOTIFY_DOWNLOAD] + ': ' + ep_name)

    def notify_subtitle_download(self, ep_name, lang):
        if sickbeard.MATTERMOST_NOTIFY_SUBTITLEDOWNLOAD:
            self._notify_MATTERMOST(common.notifyStrings[common.NOTIFY_SUBTITLE_DOWNLOAD] + ' ' + ep_name + ": " + lang)

    def notify_git_update(self, new_version="??"):
        if sickbeard.USE_MATTERMOST:
            update_text = common.notifyStrings[common.NOTIFY_GIT_UPDATE_TEXT]
            title = common.notifyStrings[common.NOTIFY_GIT_UPDATE]
            self._notify_MATTERMOST(title + " - " + update_text + new_version)

    def notify_login(self, ipaddress=""):
        if sickbeard.USE_MATTERMOST:
            update_text = common.notifyStrings[common.NOTIFY_LOGIN_TEXT]
            title = common.notifyStrings[common.NOTIFY_LOGIN]
            self._notify_MATTERMOST(title + " - " + update_text.format(ipaddress))

    def test_notify(self):
        return self._notify_MATTERMOST("This is a test notification from SickChill", force=True)

    def _send_MATTERMOST(self, message=None):
        MATTERMOST_webhook = self.MATTERMOST_WEBHOOK_URL + sickbeard.MATTERMOST_WEBHOOK.replace(self.MATTERMOST_WEBHOOK_URL, '')

        logger.log("Sending MATTERMOST message: " + message, logger.INFO)
        logger.log("Sending MATTERMOST message  to url: " + MATTERMOST_webhook, logger.INFO)

        if isinstance(message, six.text_type):
            message = message.encode('utf-8')

        headers = {b"Content-Type": b"application/json"}
        try:
            r = requests.post(MATTERMOST_webhook, data=json.dumps(dict(text=message, username="SickChillBot")), headers=headers)
            r.raise_for_status()
        except Exception as e:
            logger.log("Error Sending MATTERMOST message: " + ex(e), logger.ERROR)
            return False

        return True

    def _notify_MATTERMOST(self, message='', force=False):
        if not sickbeard.USE_MATTERMOST and not force:
            return False

        return self._send_MATTERMOST(message)
