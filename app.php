<?php

$DB_HOST = 'localhost';
$DB_USER = 'root';
$DB_PASS = '';
$DB_NAME = 'money_mgr';
$PDO     = null;
$API_TYPE   = null;
$API_METHOD = null;
$API_POST   = null;

// timezone setting
date_default_timezone_set('Asia/Tokyo');

// {{{ beforeDatabase()

function beforeDatabase() {
    global
        $DB_HOST,
        $DB_USER,
        $DB_PASS,
        $DB_NAME,
        $PDO;

    try {
        $PDO = new PDO(
            'mysql:host='.$DB_HOST.';dbname='.$DB_NAME.';charset=utf8',
            $DB_USER,
            $DB_PASS,
            array(PDO::MYSQL_ATTR_INIT_COMMAND => 'SET CHARACTER SET `utf8`')
        );
    } catch (PDOException $e) {
        // error code
        exit('database connect error: '.$e->getMessage());
    }
}

// }}}
// {{{ afterDatabase()

function afterDatabase() {
    global $PDO;
    $PDO = null;
}
// }}}
// {{{ parseAPIParams($params)

function parseAPIParams($params) {
    global
        $API_METHOD,
        $API_TYPE,
        $API_POST;

    $API_METHOD = $params['method'];
    $API_TYPE = $params['type'];
    $API_POST = (array)json_decode(file_get_contents('php://input'));

    return $API_METHOD && $API_TYPE;
}

// }}}
// {{{ createResponse($data, $error)

function createResponse($data, $error) {
    $response = array(
        'success'   => !$error,
        'total'     => count($data),
        'data'      => $data
    );
    return json_encode($response);
}

// }}}
// {{{ createInsertPrepare($sql, $data)

function createInsertPrepare($sql, $data) {
    global $PDO;

    $data['created'] = $data['modified'] = date('Y-m-d H:i:s');

    foreach($data as $k => $v) {
        if ($v) {
            $field[] = $k;
            $value[] = ':'.$k;
        }
    }

    $sql .= ' (' . implode(',', $field) . ') ';
    $sql .= ' VALUES ';
    $sql .= ' (' . implode(',', $value) . ') ';

    $rst = $PDO->prepare($sql);

    foreach($data as $k => $v) {
        if ($v) {
            $bind = ':'.$k;
            $rst->bindValue($bind, $v, PDO::PARAM_STR);
        }
    }

    return $rst;
}

// }}}
// {{{ createUpdatePrepare($sql, $data)

function createUpdatePrepare($sql, $data) {
    global $PDO;

    $data['modified'] = date('Y-m-d H:i:s');

    foreach($data as $k => $v) {
        if ($k === 'id') {
            $where[] = $k.' = '.':'.$k;
        } else if ($v) {
            $field[] = $k.' = '.':'.$k;
        }
    }

    $sql .= implode(',', $field);
    $sql .= ' WHERE ';
    $sql .= implode(',', $where);

    $rst = $PDO->prepare($sql);

    foreach($data as $k => $v) {
        if ($v) {
            $bind = ':'.$k;
            $rst->bindValue($bind, $v, PDO::PARAM_STR);
        }
    }

    return $rst;
}

// }}}
// {{{ createDeletePrepare($sql, $data)

function createDeletePrepare($sql, $data) {
    global $PDO;

    foreach($data as $k => $v) {
        if ($k === 'id') {
            $where[] = $k.' = '.':'.$k;
        }
    }

    $sql .= ' WHERE ';
    $sql .= implode(',', $where);

    $rst = $PDO->prepare($sql);

    foreach($data as $k => $v) {
        if ($v) {
            $bind = ':'.$k;
            $rst->bindValue($bind, $v, PDO::PARAM_STR);
        }
    }

    return $rst;
}

// }}}
// {{{ execute($rst, &$data, &$error)

function execute($rst, &$data, &$error) {
    global $PDO;

    try {
        $PDO->beginTransaction();
        $rst->execute();
        if (is_null($data['id'])) {
            $data['id'] = $PDO->lastInsertId();
        }
        $PDO->commit();
    } catch(PDOException $e) {
        $PDO->rollback();
        $error = true;
        $data = null;
    }
}

// }}}
// {{{ fetch($res)

function fetch($res) {
    $rows = array();
    while ($row = $res->fetch(PDO::FETCH_ASSOC)) {
        if (isset($row['date'])) {
            $row['date'] = date_create($row['date'])->format('Y-m-d');
        }
        $rows[] = $row;
    }
    return $rows;
}

// }}}
// {{{ parseParams($fields, $params)

function parseParams($fields, $params) {
    $data = array();
    foreach($fields as $k => $v) {
        if (isset($params[$v])) {
            $data[$v] = $params[$v];
        }
    }
    return $data;
}

// }}}
// {{{ parseCategoryParams($params)

function parseCategoryParams($params) {
    return parseParams(array(
        'id'    => null,
        'name'  => null,
        'type'  => null,
        'fixed' => null
    ), $params);
}

// }}}
// {{{ parseMemberParams($params)

function parseMemberParams($params) {
    return parseParams(array(
        'id'    => null,
        'name'  => null
    ), $params);
}

// }}}
// {{{ parseCreditcardParams($params)

function parseCreditcardParams($params) {
    return parseParams(array(
        'id'        => null,
        'name'      => null,
        'cutoff'    => null,
        'debit'     => null,
        'member_id' => null,
    ), $params);
}

// }}}
// {{{ parsePaymentParams($params)

function parsePaymentParams($params) {
    return parseParams(array(
        'id',
        'name',
        'category_id',
        'price',
        'member_id',
        'creditcard_id',
        'date',
        'note',
    ), $params);
}

// }}}
// {{{ parseRevenueParams($params)

function parseRevenueParams($params) {
    return parseParams(array(
        'id',
        'name',
        'category_id',
        'price',
        'total_price',
        'member_id',
        'date',
        'note',
    ), $params);
}

// }}}
// {{{ readCategory()

function readCategory() {
    global $PDO;
    $sql = 'SELECT * FROM tbl_categories';
    $res = $PDO->query($sql);
    $rows= fetch($res);
    return createResponse($rows, false);
}

// }}}
// {{{ readMember()

function readMember() {
    global $PDO;
    $rows = array();
    $sql = 'SELECT * FROM tbl_members';
    $res = $PDO->query($sql);
    while ($row = $res->fetch(PDO::FETCH_ASSOC)) {
        if (isset($row['date'])) {
            $row['date'] = date_create($row['date'])->format('Y-m-d');
        }
        $rows[] = $row;
    }
    return createResponse($rows, false);
}

// }}}
// {{{ readCreditcard()

function readCreditcard() {
    global $PDO;
    $rows = array();
    $sql = 'SELECT * FROM tbl_creditcards';
    $res = $PDO->query($sql);
    while ($row = $res->fetch(PDO::FETCH_ASSOC)) {
        if (isset($row['date'])) {
            $row['date'] = date_create($row['date'])->format('Y-m-d');
        }
        $rows[] = $row;
    }
    return createResponse($rows, false);
}

// }}}
// {{{ readPayment()

function readPayment() {
    global $PDO;
    $rows = array();
    $sql = 'SELECT * FROM tbl_payments';
    $res = $PDO->query($sql);
    while ($row = $res->fetch(PDO::FETCH_ASSOC)) {
        if (isset($row['date'])) {
            $row['date'] = date_create($row['date'])->format('Y-m-d');
        }
        $rows[] = $row;
    }
    return createResponse($rows, false);
}

// }}}
// {{{ readRevenue()

function readRevenue() {
    global $PDO;
    $rows = array();
    $sql = 'SELECT * FROM tbl_revenues';
    $res = $PDO->query($sql);
    while ($row = $res->fetch(PDO::FETCH_ASSOC)) {
        if (isset($row['date'])) {
            $row['date'] = date_create($row['date'])->format('Y-m-d');
        }
        $rows[] = $row;
    }
    return createResponse($rows, false);
}

// }}}
// {{{ createCategory($params)

function createCategory($params) {
    global $PDO;

    $data  = parseCategoryParams($params);
    $error = false;
    $sql   = 'INSERT INTO tbl_categories';
    $rst   = createInsertPrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ createMember($params)

function createMember($params) {
    global $PDO;

    $data  = parseMemberParams($params);
    $error = false;
    $sql   = 'INSERT INTO tbl_members';
    $rst   = createInsertPrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ createCreditcard($params)

function createCreditcard($params) {
    global $PDO;

    $data  = parseCreditcardParams($params);
    $error = false;
    $sql   = 'INSERT INTO tbl_creditcards';
    $rst   = createInsertPrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ createPayment($params)

function createPayment($params) {
    global $PDO;

    $data  = parsePaymentParams($params);
    $error = false;
    $sql   = 'INSERT INTO tbl_payments';
    $rst   = createInsertPrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ createRevenue($params)

function createRevenue($params) {
    global $PDO;

    $data  = parseRevenueParams($params);
    $error = false;
    $sql   = 'INSERT INTO tbl_revenues';
    $rst   = createInsertPrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ updateCategory($params)

function updateCategory($params) {
    global $PDO;

    $data  = parseCategoryParams($params);
    $error = false;
    $sql   = 'UPDATE tbl_categories SET ';
    $rst   = createUpdatePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ updateMember($params)

function updateMember($params) {
    global $PDO;

    $data  = parseMemberParams($params);
    $error = false;
    $sql   = 'UPDATE tbl_members SET ';
    $rst   = createUpdatePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ updateCreditcard($params)

function updateCreditcard($params) {
    global $PDO;

    $data  = parseCreditcardParams($params);
    $error = false;
    $sql   = 'UPDATE tbl_creditcards SET ';
    $rst   = createUpdatePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ updatePayment($params)

function updatePayment($params) {
    global $PDO;

    $data  = parsePaymentParams($params);
    $error = false;
    $sql   = 'UPDATE tbl_payments SET ';
    $rst   = createUpdatePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ updateRevenue($params)

function updateRevenue($params) {
    global $PDO;

    $data  = parseRevenueParams($params);
    $error = false;
    $sql   = 'UPDATE tbl_revenues SET ';
    $rst   = createUpdatePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ deleteCategory($params)

function deleteCategory($params) {
    global $PDO;

    $data  = parseCategoryParams($params);
    $error = false;
    $sql   = 'DELETE FROM tbl_categories ';
    $rst   = createDeletePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ deleteMember($params)

function deleteMember($params) {
    global $PDO;

    $data  = parseMemberParams($params);
    $error = false;
    $sql   = 'DELETE FROM tbl_members ';
    $rst   = createDeletePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ deleteCreditcard($params)

function deleteCreditcard($params) {
    global $PDO;

    $data  = parseCreditcardParams($params);
    $error = false;
    $sql   = 'DELETE FROM tbl_creditcards ';
    $rst   = createDeletePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ deletePayment($params)

function deletePayment($params) {
    global $PDO;

    $data  = parsePaymentParams($params);
    $error = false;
    $sql   = 'DELETE FROM tbl_payments ';
    $rst   = createDeletePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}
// {{{ deleteRevenue($params)

function deleteRevenue($params) {
    global $PDO;

    $data  = parseRevenueParams($params);
    $error = false;
    $sql   = 'DELETE FROM tbl_revenues ';
    $rst   = createDeletePrepare($sql, $data);

    execute($rst, $data, $error);

    return createResponse(array($data), $error);
}

// }}}

beforeDatabase();

if (!parseAPIParams($_GET)) {
    // error code
    exit;
}

$API_FUNC = $API_METHOD . ucfirst($API_TYPE);

try {
    header('Content-Type: application/json; charset=utf-8');
    echo $API_FUNC($API_POST);
} catch(Exception $e) {
    exit;
}

afterDatabase();

