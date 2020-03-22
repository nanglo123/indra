from nose.plugins.attrib import attr
from gilda import ground
from indra.sources import hypothesis
from indra.sources.hypothesis.processor import HypothesisProcessor, \
    parse_context_entry, parse_grounding_entry, get_text_refs


@attr('nonpublic')
def test_process_indra_annnotations():
    hp = hypothesis.process_annotations()
    assert hp.statements
    for stmt in hp.statements:
        print(stmt)
        print(stmt.evidence[0])


def test_get_text_refs_pmid():
    url = 'https://www.ncbi.nlm.nih.gov/pubmed/32196952'
    refs = get_text_refs(url)
    assert refs.get('PMID') == '32196952', refs
    assert refs.get('URL') == url, refs


def test_get_text_refs_pmcid():
    url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7071777/'
    refs = get_text_refs(url)
    assert refs.get('PMCID') == 'PMC7071777', refs
    assert refs.get('URL') == url, refs


def test_parse_grounding_entry():
    entry = '[a and b] -> CHEBI:CHEBI:1234|PUBCHEM:5678'
    grounding = parse_grounding_entry(entry)
    assert grounding == {'a and b': {'CHEBI': 'CHEBI:1234',
                                     'PUBCHEM': '5678'}}, grounding


def test_parse_invalid_grounding_entry():
    entries = ['xxx', '[xxx]->a', 'xxx -> a', 'xxx -> a:1&b:4']
    for entry in entries:
        assert parse_grounding_entry(entry) is None


def test_parse_context_entry():
    context_dict = parse_context_entry('Cell type: antigen presenting cells',
                                       ground, 'antigen presenting cells')
    assert len(context_dict) == 1
    assert 'cell_type' in context_dict
    ref_context = context_dict['cell_type']
    assert ref_context.name == 'Antigen-Presenting Cells', ref_context
    assert ref_context.db_refs.get('MESH') == 'D000938'
    assert ref_context.db_refs.get('TEXT') == 'antigen presenting cells'


def test_parse_invalid_context_entry():
    entries = ['xxx: yyy', 'Disease:something', 'xxx']
    for entry in entries:
        assert parse_context_entry(entry, ground) is None


def test_parse_ungrounded_context_entry():
    entry = 'Cell type: CD4+ T-cells'
    context_dict = parse_context_entry(entry, ground)
    assert len(context_dict['cell_type'].db_refs) == 1, \
        context_dict['cell_type'].db_refs
    assert context_dict['cell_type'].db_refs['TEXT'] == \
        'CD4+ T-cells', context_dict['cell_type'].db_refs
