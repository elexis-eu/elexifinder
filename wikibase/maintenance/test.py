import wget

url = "https://raw.githubusercontent.com/elexis-eu/elexifinder/master/elexifinder/collection-images/collection_11_videolectures.jpg"

#url="https://github.com/elexis-eu/elexifinder/tree/master/elexifinder/collection-images"

download = wget.download(url)

print(download)

import github
g = github.Github("dlindem", "Mad2026192")
repo = g.get_user().get_repo( "elexifinder" )
print(repo.get_dir_contents("elexifinder/collection-images"))
