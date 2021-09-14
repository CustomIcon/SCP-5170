import ujson as json
import os
import urllib.request
import aiohttp


class repo_info:
    repo = None
    target_dir = None
    branch = None


class api_urls:
    recursive = 'https://api.github.com/repos/{}/git/trees/{}?recursive=1'
    no_recursive = 'https://api.github.com/repos/{}/git/trees/{}'


class OctodirException(Exception):
    pass


def mkdirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)


class Octodir:
    def __init__(self, folder_url, output_folder):
        super().__init__()
        self.folder_url = folder_url
        self.output_folder = output_folder

        self.repo = None
        self.target_dir = None
        self.branch = None

    def __get_raw_url(
        self,
        file_path: str,
        url: str,
    ):
        tmp_url = url.replace(
            'https://api.github.com/repos/',
            'https://raw.githubusercontent.com/',
        )
        tmp_url = tmp_url.split('/git/blobs/')[0]
        tmp_url = tmp_url + '/' + self.branch + '/' + file_path

        return tmp_url

    async def __get_repo_tree(self):
        async with aiohttp.ClientSession() as ses:
            api = await ses.get(
                api_urls.recursive.format(
                    self.repo,
                    self.branch,
                ),
            )
        files = json.loads((await api.read()).decode('utf-8'))
        output = []
        location = {}
        for (k, i) in enumerate(files['tree']):
            # If the target dir is in file path, that file
            # is inside target folder
            if self.target_dir in i['path']:
                if i['type'] == 'blob':
                    tmp = [i['path']]
                    tmp += [self.__get_raw_url(tmp[0], i['url'])]
                    output.append(tmp)
                else:
                    location[i['path']] = k
        files = output
        location = location
        return (files, location)

    def __scrutinize_url(
        self,
        folder_url: str,
    ):
        try:
            cutted_url = folder_url.replace('https://github.com/', '')
            splitted_url = cutted_url.split('/')

            owner = splitted_url[0]
            repo = splitted_url[1]
            branch = splitted_url[3]

            target_dir = [item for item in splitted_url[4:]]

            repo_data = repo_info()
            repo_data.repo = owner + '/' + repo
            repo_data.branch = branch
            repo_data.target_dir = '/'.join(target_dir)

            return repo_data
        except IndexError:
            raise IndexError('Invalid repo url')

    async def __api_response(self):
        repo_data = self.__scrutinize_url(self.folder_url)
        async with aiohttp.ClientSession() as ses:
            api = await ses.get(
                api_urls.no_recursive.format(
                    repo_data.repo, repo_data.branch,
                ),
            )
        return json.loads((await api.read()).decode('utf-8'))

    def __check_valid_output(self):
        if os.path.isdir(self.output_folder):
            return True
        else:
            raise OctodirException('Invalid output directory')

    async def __download(
        self,
        target_folder='*',
        recursive=True
    ):
        data = await self.__get_repo_tree()
        if target_folder == '*':
            start = 0
        else:
            tmp_target = target_folder.replace('./', '').replace('../', '')
            tmp_target = (
                tmp_target if tmp_target[-1] != '/'
                else tmp_target[:-1]
            )
            start = data[1][target_folder]
        for i in data[0][start:]:
            ndir = i[0].replace(
                self.target_dir, self.target_dir.split('/')[-1:][0],
            )
            if recursive or ndir.split(target_folder)[1].count('/') \
                    <= 1:
                # Check output dir variable
                mkdirs(os.path.join(self.output_folder, os.path.dirname(ndir)))
                urllib.request.urlretrieve(
                    i[1], os.path.join(self.output_folder, ndir),
                )

    async def dowload_folder(self):
        check_repo = await self.__api_response()
        if 'message' in check_repo:
            raise OctodirException(check_repo['message'])
        if self.__check_valid_output() is True:
            scrutinized_url = self.__scrutinize_url(self.folder_url)
            self.repo = scrutinized_url.repo
            self.target_dir = scrutinized_url.target_dir
            self.branch = scrutinized_url.branch
            return await self.__download()
