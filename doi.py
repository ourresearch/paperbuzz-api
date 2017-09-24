import requests
from source import make_event_source
from event import CedEvent
from event import UnpaywallEvent


metadata = {
    "DOI": "10.7717/peerj.3828",
    "ISSN": [
      "2167-8359"
    ],
    "URL": "http://dx.doi.org/10.7717/peerj.3828",
    "abstract": "<jats:p>The phylogeny of the Salmonidae family, the only living one of the Order Salmoniformes, remains still unclear because of several reasons. Such reasons include insufficient taxon sampling and/or DNA information. The use of complete mitochondrial genomes (mitogenomics) could provide some light on it, but despite the high number of mitogenomes of species belonging to this family published during last years, an integrative work containing all this information has not been done. In this work, the phylogeny of 46 Salmonidae species was inferred from their mitogenomic sequences. Results include a Bayesian molecular-dated phylogenetic tree with very high statistical support showing Coregoninae and Salmoninae as sister subfamilies, as well as several new phylogenetic relationships among species and genus of the family. All these findings contribute to improve our understanding of the Salmonidae systematics and could have consequences on related evolutionary studies, as well as highlight the importance of revisiting phylogenies with integrative studies.</jats:p>",
    "alternative-id": [
      "10.7717/peerj.3828"
    ],
    "article-number": "e3828",
    "author": [
      {
        "affiliation": [
          {
            "name": "Department of Biodiversity and Evolutionary Biology, National Museum of Natural Sciences (CSIC),  Madrid, Spain"
          }
        ],
        "family": "Horreo",
        "given": "Jose L."
      }
    ],
    "container-title": "PeerJ",
    "content-domain": {
      "crossmark-restriction": False,
      "domain": []
    },
    "created": {
      "date-parts": [
        [
          2017,
          9,
          18
        ]
      ],
      "date-time": "2017-09-18T18:56:07Z",
      "timestamp": 1505760967000
    },
    "crossref_url": "https://api.crossref.org/works/10.7717/peerj.3828/transform/application/vnd.citationstyles.csl+json",
    "deposited": {
      "date-parts": [
        [
          2017,
          9,
          18
        ]
      ],
      "date-time": "2017-09-18T18:56:10Z",
      "timestamp": 1505760970000
    },
    "funder": [
      {
        "award": [
          "IJCI-2015-23618"
        ],
        "name": "MINECO Spanish postdoctoral grant Juan de la Cierva-Incorporaci\u00f3n"
      }
    ],
    "indexed": {
      "date-parts": [
        [
          2017,
          9,
          18
        ]
      ],
      "date-time": "2017-09-18T19:10:07Z",
      "timestamp": 1505761807491
    },
    "is-referenced-by-count": 0,
    "issued": {
      "date-parts": [
        [
          2017,
          9,
          18
        ]
      ]
    },
    "license": [
      {
        "URL": "http://creativecommons.org/licenses/by/4.0/",
        "content-version": "vor",
        "delay-in-days": 0,
        "start": {
          "date-parts": [
            [
              2017,
              9,
              18
            ]
          ],
          "date-time": "2017-09-18T00:00:00Z",
          "timestamp": 1505692800000
        }
      }
    ],
    "link": [
      {
        "URL": "https://peerj.com/articles/3828.pdf",
        "content-type": "application/pdf",
        "content-version": "vor",
        "intended-application": "text-mining"
      },
      {
        "URL": "https://peerj.com/articles/3828.xml",
        "content-type": "application/xml",
        "content-version": "vor",
        "intended-application": "text-mining"
      },
      {
        "URL": "https://peerj.com/articles/3828.html",
        "content-type": "text/html",
        "content-version": "vor",
        "intended-application": "text-mining"
      },
      {
        "URL": "https://peerj.com/articles/3828.pdf",
        "content-type": "unspecified",
        "content-version": "vor",
        "intended-application": "similarity-checking"
      }
    ],
    "member": "4443",
    "original-title": [],
    "page": "e3828",
    "prefix": "10.7717",
    "published-online": {
      "date-parts": [
        [
          2017,
          9,
          18
        ]
      ]
    },
    "publisher": "PeerJ",
    "reference": [
      {
        "DOI": "10.1016/j.ympev.2013.07.026",
        "article-title": "Genome duplication and multiple evolutionary origins of complex migratory behavior in Salmonidae",
        "author": "Alexandrou",
        "doi-asserted-by": "publisher",
        "first-page": "514",
        "journal-title": "Molecular Phylogenetics and Evolution",
        "key": "10.7717/peerj.3828/ref-1",
        "volume": "69",
        "year": "2013"
      },
      {
        "DOI": "10.1073/pnas.102164299",
        "article-title": "Mammalian mitogenomic relationships and the root of the eutherian tree",
        "author": "Arnason",
        "doi-asserted-by": "publisher",
        "first-page": "8151",
        "journal-title": "Proceedings of the National Academy of Sciences of the United States of America",
        "key": "10.7717/peerj.3828/ref-2",
        "volume": "11",
        "year": "2002"
      },
      {
        "DOI": "10.1080/23802359.2016.1166080",
        "article-title": "Complete mitochondrial genome of thestone char Salvelinus kuznetzovi (Salmoniformes, Salmonidae)",
        "author": "Balakirev",
        "doi-asserted-by": "publisher",
        "first-page": "287",
        "journal-title": "Mitochondrial DNA Part B",
        "key": "10.7717/peerj.3828/ref-3",
        "volume": "1",
        "year": "2016"
      },
      {
        "DOI": "10.3109/19401736.2015.1111358",
        "article-title": "Complete mitochondrial genome of the Kamchatka grayling Thymallus mertensii (Salmoniformes, Salmonidae)",
        "author": "Balakirev",
        "doi-asserted-by": "publisher",
        "first-page": "135",
        "journal-title": "Mitochondrial DNA Part A",
        "key": "10.7717/peerj.3828/ref-4",
        "volume": "28",
        "year": "2017"
      },
      {
        "DOI": "10.1371/journal.pcbi.1003537",
        "article-title": "BEAST 2: a software platform for Bayesian evolutionary analysis",
        "author": "Bouckaert",
        "doi-asserted-by": "publisher",
        "first-page": "e1003537",
        "journal-title": "PLOS Computational Biology",
        "key": "10.7717/peerj.3828/ref-5",
        "volume": "10",
        "year": "2014"
      },
      {
        "DOI": "10.1016/j.gene.2013.07.068",
        "article-title": "Pike and salmon as sister taxa: detailed intraclade resolution and divergence time estimation of Esociformes + Salmoniformes based on whole mitochondrial genome sequences",
        "author": "Campbell",
        "doi-asserted-by": "publisher",
        "first-page": "57",
        "journal-title": "Gene",
        "key": "10.7717/peerj.3828/ref-6",
        "volume": "530",
        "year": "2013"
      },
      {
        "DOI": "10.1371/journal.pone.0046662",
        "article-title": "Framing the Salmonidae family phylogenetic portrait: a more complete picture from increased taxon sampling",
        "author": "Cr\u00eate-Lafreni\u00e8re",
        "doi-asserted-by": "publisher",
        "first-page": "e46662",
        "journal-title": "PLOS ONE",
        "key": "10.7717/peerj.3828/ref-7",
        "volume": "7",
        "year": "2012"
      },
      {
        "DOI": "10.1139/e04-100",
        "article-title": "Fossil biotas from the Okanagan Highlands, southern British Columbia and northeastern Washington State: climates and ecosystems across an Eocene landscape",
        "author": "Greenwood",
        "doi-asserted-by": "publisher",
        "first-page": "167",
        "journal-title": "Canadian Journal of Earth Sciences",
        "key": "10.7717/peerj.3828/ref-8",
        "volume": "42",
        "year": "2005"
      },
      {
        "article-title": "Taxon sampling and the accuracy of phylogenetic analyses",
        "author": "Heath",
        "first-page": "237",
        "journal-title": "Journal of Syestematics and Evolution",
        "key": "10.7717/peerj.3828/ref-9",
        "volume": "46",
        "year": "2008"
      },
      {
        "DOI": "10.1080/23802359.2016.1166084",
        "article-title": "Complete mitochondrial genome of Oncorhynchus masou formosanus (Jordan & Oshima, 1919) (Pisces, Salmonidae)",
        "author": "Ho",
        "doi-asserted-by": "publisher",
        "first-page": "295",
        "journal-title": "Mitochondrial DNA Part B",
        "key": "10.7717/peerj.3828/ref-10",
        "volume": "1",
        "year": "2016"
      },
      {
        "DOI": "10.1111/j.1420-9101.2012.02622.x",
        "article-title": "\u2018Representative Genes\u2019, is it OK to use a small amount of data to obtain a phylogeny that is at least close to the True tree?",
        "author": "Horreo",
        "doi-asserted-by": "publisher",
        "first-page": "2661",
        "journal-title": "Journal of Evolutionary Biology",
        "key": "10.7717/peerj.3828/ref-11",
        "volume": "25",
        "year": "2012"
      },
      {
        "DOI": "10.1186/1471-2148-13-5",
        "article-title": "Cnidarian phylogenetic relationships as revealed by mitogenomics",
        "author": "Kayal",
        "doi-asserted-by": "publisher",
        "first-page": "5",
        "journal-title": "BMC Evolutionary Biology",
        "key": "10.7717/peerj.3828/ref-12",
        "volume": "13",
        "year": "2013"
      },
      {
        "DOI": "10.1093/sysbio/syv005",
        "article-title": "Ancestral state reconstruction, rate heterogenetiy and the evolution of reptile viviparity",
        "author": "King",
        "doi-asserted-by": "publisher",
        "first-page": "532",
        "journal-title": "Systematic Biology",
        "key": "10.7717/peerj.3828/ref-13",
        "volume": "64",
        "year": "2015"
      },
      {
        "DOI": "10.1093/bioinformatics/btu531",
        "article-title": "AliView: a fast and lightweight alignment viewer and editor for large data sets",
        "author": "Larsson",
        "doi-asserted-by": "publisher",
        "first-page": "3276",
        "journal-title": "Bioinformatics",
        "key": "10.7717/peerj.3828/ref-14",
        "volume": "30",
        "year": "2014"
      },
      {
        "DOI": "10.1186/1471-2164-11-279",
        "article-title": "Salmo salar and Esox lucius full-length cDNA sequences reveal changes in evolutionary pressures on a post-tetraploidization genome",
        "author": "Leong",
        "doi-asserted-by": "publisher",
        "first-page": "279",
        "journal-title": "BMC Genomics",
        "key": "10.7717/peerj.3828/ref-15",
        "volume": "11",
        "year": "2010"
      },
      {
        "DOI": "10.1080/23802359.2016.1192501",
        "article-title": "The complete mitochondrial genome of Salmo trutta fario Linnaeus (Salmoniformes, Salmoninae)",
        "author": "Li",
        "doi-asserted-by": "publisher",
        "first-page": "491",
        "journal-title": "Mitochondrial DNA Part B",
        "key": "10.7717/peerj.3828/ref-16",
        "volume": "1",
        "year": "2016"
      },
      {
        "DOI": "10.1080/23802359.2016.1229589",
        "article-title": "The complete mitochondrial DNA sequence of Xinjiang arctic grayling Thymallus arcticus grubei",
        "author": "Liu",
        "doi-asserted-by": "publisher",
        "first-page": "724",
        "journal-title": "Mitochondrial DNA Part B",
        "key": "10.7717/peerj.3828/ref-17",
        "volume": "1",
        "year": "2016"
      },
      {
        "DOI": "10.3109/19401736.2015.1079824",
        "article-title": "Phylogeny and dating of divergences within the genus Thymallus (Salmonidae: Thymallinae) using complete mitochondrial genomes",
        "author": "Ma",
        "doi-asserted-by": "publisher",
        "first-page": "3602",
        "journal-title": "Mitochondrial DNA Part A",
        "key": "10.7717/peerj.3828/ref-18",
        "volume": "27",
        "year": "2016"
      },
      {
        "DOI": "10.1098/rspb.2013.2881",
        "article-title": "A well-constrained estimate for the timing of the salmonid whole genome duplication reveals major decoupling from species diversification",
        "author": "Macqueen",
        "doi-asserted-by": "publisher",
        "first-page": "20132881",
        "journal-title": "Proceedings of the Royal Society B",
        "key": "10.7717/peerj.3828/ref-19",
        "volume": "281",
        "year": "2014"
      },
      {
        "DOI": "10.1007/s10228-014-0440-9",
        "article-title": "The mitogenomic contributions to molecular phylogenetics and evolution of fishes: a 15-year retrospect",
        "author": "Miya",
        "doi-asserted-by": "publisher",
        "first-page": "29",
        "journal-title": "Ichthyological Research",
        "key": "10.7717/peerj.3828/ref-20",
        "volume": "62",
        "year": "2015"
      },
      {
        "DOI": "10.1073/pnas.1206625109",
        "article-title": "Resolution of ray-finned fish phylogeny and timing of diversification",
        "author": "Near",
        "doi-asserted-by": "publisher",
        "first-page": "13698",
        "journal-title": "Proceedings of the National Academy of Sciences of the United States of America",
        "key": "10.7717/peerj.3828/ref-21",
        "volume": "109",
        "year": "2012"
      },
      {
        "DOI": "10.1093/molbev/msr014",
        "article-title": "Evolution of modern birds revealed by mitogenomics: timing the radiation and origin of major orders",
        "author": "Pacheco",
        "doi-asserted-by": "publisher",
        "first-page": "1927",
        "journal-title": "Molecular Biology and Evolution",
        "key": "10.7717/peerj.3828/ref-22",
        "volume": "28",
        "year": "2011"
      },
      {
        "DOI": "10.1186/1748-7188-9-4",
        "article-title": "Assessing the efficiency of multiple sequence alignment programs",
        "author": "Pais",
        "doi-asserted-by": "publisher",
        "first-page": "4",
        "journal-title": "Algorithms for Molecular Biology",
        "key": "10.7717/peerj.3828/ref-23",
        "volume": "9",
        "year": "2014"
      },
      {
        "DOI": "10.1093/molbev/msn083",
        "article-title": "jModelTest: phylogenetic model averaging",
        "author": "Posada",
        "doi-asserted-by": "publisher",
        "first-page": "1253",
        "journal-title": "Molecular Biology and Evolution",
        "key": "10.7717/peerj.3828/ref-24",
        "volume": "25",
        "year": "2008"
      },
      {
        "DOI": "10.3109/19401736.2015.1101565",
        "article-title": "The complete mitogenome of brown trout (Salmo trutta fario) and its phylogeny",
        "author": "Sahoo",
        "doi-asserted-by": "publisher",
        "first-page": "4563",
        "journal-title": "Mitochondrial DNA Part A",
        "key": "10.7717/peerj.3828/ref-25",
        "volume": "27",
        "year": "2016"
      },
      {
        "DOI": "10.1134/S1022795413060112",
        "article-title": "Phylogeny of salmonids (Salmoniformes: Salmonidae) and its molecular dating: analysis of mtDNA data",
        "author": "Shedko",
        "doi-asserted-by": "publisher",
        "first-page": "623",
        "journal-title": "Russian Journal of Genetics",
        "key": "10.7717/peerj.3828/ref-26",
        "volume": "49",
        "year": "2013"
      },
      {
        "DOI": "10.1186/1471-2164-11-371",
        "article-title": "Comparative mitogenomics of Braconidae (Insecta: Hymenoptera) and the phylogenetic utility of mitochondrial genomes with special reference to Holometabolous insects",
        "author": "Wei",
        "doi-asserted-by": "publisher",
        "first-page": "371",
        "journal-title": "BMC Genomics",
        "key": "10.7717/peerj.3828/ref-27",
        "volume": "11",
        "year": "2010"
      },
      {
        "DOI": "10.1080/23802359.2016.1186507",
        "article-title": "Complete mitochondrial genome of Coregonus chadary Dybowski",
        "author": "Xue",
        "doi-asserted-by": "publisher",
        "first-page": "459",
        "journal-title": "Mitochondrial DNA Part B",
        "key": "10.7717/peerj.3828/ref-28",
        "volume": "1",
        "year": "2016"
      },
      {
        "DOI": "10.1093/bioinformatics/btw412",
        "article-title": "Application of the MAFFT sequence alignment program to large data\u2013reexamination of the usefulness of chained guide trees",
        "author": "Yamada",
        "doi-asserted-by": "publisher",
        "first-page": "3246",
        "journal-title": "Bioinformatics",
        "key": "10.7717/peerj.3828/ref-29",
        "volume": "32",
        "year": "2016"
      },
      {
        "DOI": "10.1111/j.1095-8649.2009.02494.x",
        "article-title": "Grayling (Thymallinae) phylogeny within salmonids: complete mitochondrial DNA sequences of Thymallus arcticus and Thymallus thymallus",
        "author": "Yasuike",
        "doi-asserted-by": "publisher",
        "first-page": "395",
        "journal-title": "Journal of Fish Biology",
        "key": "10.7717/peerj.3828/ref-30",
        "volume": "76",
        "year": "2010"
      },
      {
        "DOI": "10.1016/j.gene.2015.07.049",
        "article-title": "The complete mitochondrial genome of Brachymystax lenok tsinlingensis (Salmoninae, Salmonidae) and its intraspecific variation",
        "author": "Yu",
        "doi-asserted-by": "publisher",
        "first-page": "246",
        "journal-title": "Gene",
        "key": "10.7717/peerj.3828/ref-31",
        "volume": "573",
        "year": "2015"
      }
    ],
    "reference-count": 31,
    "references-count": 31,
    "relation": {
      "cites": []
    },
    "score": 1.0,
    "short-title": [],
    "source": "Crossref",
    "subject": [
      "General Biochemistry, Genetics and Molecular Biology",
      "General Neuroscience",
      "General Agricultural and Biological Sciences",
      "General Medicine"
    ],
    "subtitle": [],
    "title": "Revisiting the mitogenomic phylogeny of Salmoninae: new insights thanks to recent sequencing advances",
    "type": "article-journal",
    "volume": "5"
  }

open_access = {
    "best_oa_location": {
      "evidence": "hybrid (via crossref license)",
      "host_type": "publisher",
      "is_best": True,
      "license": "cc-by",
      "updated": "2017-09-24T00:09:23.763770",
      "url": "http://doi.org/10.7717/peerj.3828",
      "version": "publishedVersion"
    },
    "data_standard": 1,
    "doi": "10.7717/peerj.3828",
    "is_oa": True,
    "journal_is_oa": False,
    "journal_issns": "2167-8359",
    "journal_name": "PeerJ",
    "oa_locations": [
      {
        "evidence": "hybrid (via crossref license)",
        "host_type": "publisher",
        "is_best": True,
        "license": "cc-by",
        "updated": "2017-09-24T00:09:23.763770",
        "url": "http://doi.org/10.7717/peerj.3828",
        "version": "publishedVersion"
      }
    ],
    "oadoi_url": "https://api.oadoi.org/v2/10.7717/peerj.3828",
    "publisher": "PeerJ",
    "title": "Revisiting the mitogenomic phylogeny of Salmoninae: new insights thanks to recent sequencing advances",
    "updated": "2017-09-24T00:09:23.754159",
    "x_reported_noncompliant_copies": [],
    "year": 2017
  }

sources = [
{
"events": [],
"events_count": 29,
"events_count_by_day": [],
"source_id": "twitter"
},
{
"events": [],
"source_id": "unpaywall_views"
}
]



class Doi(object):

    def __init__(self, doi):
        self.doi = doi
        self.metadata = CrossrefMetadata(self.doi)
        self.open_access = OaDoi(self.doi)
        self.altmetrics = AltmetricsForDoi(self.doi)
        self.unpaywall_views = UnpaywallViewsForDoi(self.doi)

    def get(self):
        self.metadata.get()
        self.open_access.get()
        self.altmetrics.get()
        self.unpaywall_views.get()

    def to_dict(self):
        altmetrics_value = self.altmetrics.to_dict()
        altmetrics_value["sources"] += [{
                "source_id": "unpaywall_views",
                "events": self.unpaywall_views.to_dict()}]
        ret = {
            "doi": self.doi,
            "altmetrics":  altmetrics_value,
            "metadata": self.metadata.to_dict(),
            "open_access": self.open_access.to_dict(),
            "unpaywall_views": self.unpaywall_views.to_dict()
        }
        return ret


    def to_dict_hotness(self):
        ret = {
            "doi": self.doi,
            "metadata": metadata,
            "open_access": open_access,
            "sources": sources,
        }
        return ret

class AltmetricsForDoi(object):
    def __init__(self, doi):
        self.doi = doi
        self.ced_url = "http://query.eventdata.crossref.org/events?rows=10000&filter=from-collected-date:1990-01-01,until-collected-date:2099-01-01,obj-id:{}".format(
            self.doi
        )
        self.events = []
        self.sources = []

    def get(self):
        ced_events = self._get_ced_events()
        for ced_event in ced_events:
            self.add_event(ced_event)

    def add_event(self, ced_event):
        source_id = ced_event["source_id"]

        # get the correct source for this event
        my_source = None
        for source in self.sources:
            if source.id == source_id:
                my_source = source
                break

        # we don't have this source for this DOI.
        # make it and add it to the list
        if my_source is None:
            my_source = make_event_source(source_id)
            self.sources.append(my_source)

        # this source exists now for sure because we either found it or made it
        # add the event to the source.
        my_source.add_event(ced_event)


    def _get_ced_events(self):
        """
        Handy test data:
        10.2190/EC.43.3.f                       # no events
        10.1371/journal.pone.0000308            # many events, incl lots of wiki
        """

        event_objs = CedEvent.query.filter(CedEvent.doi==self.doi).all()
        event_dicts = [event.api_raw for event in event_objs]
        return event_dicts

        return event_dicts

    def to_dict(self):
        ret = {
            "crossref_event_data_url": self.ced_url,
            "sources": [s.to_dict() for s in self.sources]
        }
        return ret



class UnpaywallViewsForDoi(object):
    def __init__(self, doi):
        self.doi = doi

    def get(self):
        event_objs = UnpaywallEvent.query.filter(UnpaywallEvent.doi==self.doi).all()
        event_dicts = [event.api_dict() for event in event_objs]
        return event_dicts

    def to_dict(self):
        ret = self.get()
        return ret


class OaDoi(object):
    def __init__(self, doi):
        self.doi = doi
        self.url = u"https://api.oadoi.org/v2/{}".format(doi)
        self.data = {}

    def get(self):
        r = requests.get(self.url)
        self.data = r.json()

    def to_dict(self):
        self.data["oadoi_url"] = self.url
        return self.data



class CrossrefMetadata(object):
    def __init__(self, doi):
        self.doi = doi
        self.url = u"https://api.crossref.org/works/{}/transform/application/vnd.citationstyles.csl+json".format(doi)
        self.data = {}

    def get(self):
        r = requests.get(self.url)
        self.data = r.json()

    def to_dict(self):
        self.data["crossref_url"] = self.url
        return self.data

