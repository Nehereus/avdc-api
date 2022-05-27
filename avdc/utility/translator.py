from avdc.model.metadata import Metadata
from avdc.utility.deepL_api import translate
import os

enableTranslation = False
translationTargetLang = "EN-US"
def GetENV():
    global enableTranslation
    global translationTargetLang
    # get information from environment variable about weather enable translation
    try:

        enableTranslation = os.environ['ENABLE_TRANSLATION'] == "True"
    except:
        pass

    if enableTranslation:
        try:
            translationTargetLang = os.environ['TARGET_LANG']
        except:
            pass

def TranslateMetadata(metadata: Metadata):
    GetENV()
    if enableTranslation:
        if isinstance(metadata, Metadata):
            tmp = metadata
            for i, x in enumerate(tmp.genres):
                tmp.genres[i] = translate(x, translationTargetLang)
            if not tmp.overview == "":
                tmp.overview = translate(tmp.overview, translationTargetLang)
            tmp.title = translate(tmp.title, translationTargetLang)
            return tmp
    else:
        return metadata
