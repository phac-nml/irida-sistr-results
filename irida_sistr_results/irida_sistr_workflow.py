WORKFLOW_IDS = {
    '0.1': 'e559af58-a560-4bbd-997e-808bfbe026e2',
    '0.2': 'e8f9cc61-3264-48c6-81d9-02d9e84bccc7',
    '0.3': '92ecf046-ee09-4271-b849-7a82625d6b60',
    None: None
}
WORKFLOW_VERSIONS = dict((v, k) for (k, v) in WORKFLOW_IDS.items())

def workflow_id_to_version(workflow_id):
    """
    Converts an IRIDA workflow id to a version number.
    :param workflow_id: The workflow id.
    :return: The version number for the workflow.
    """
    return WORKFLOW_VERSIONS[workflow_id]

def workflow_version_to_id(workflow_version):
    """
    Converts an IRIDA workflow version to an id.
    :param workflow_version: The workflow version.
    :return: The id of the workflow.
    """
    return WORKFLOW_IDS[workflow_version]