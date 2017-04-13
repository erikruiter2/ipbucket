from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import validates
from database import Base
from sqlalchemy.orm import relationship


class IPv4Network(Base):
    __tablename__ = 'ipv4network'
    id = Column(Integer, primary_key=True, nullable=False)
    ip_domain_id = Column(Integer, nullable=False)
    ip = Column(Integer, nullable=False)
    mask = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    comment = Column(String(1024))

    __table_args__ = (UniqueConstraint('ip_domain_id', 'ip', 'mask'),)

    @validates('mask')
    def validate_mask(self, key, mask):
        if (mask < 0) or (mask > 32):
            raise ValueError('Mask must be value between 0 and 32')
        return mask

    @validates('name')
    def validate_name(self, key, name):
        if len(name) == 0:
            raise ValueError('network name must not be empty')
        return name

    def __init__(self, ip_domain_id=None, name=None, ip=None, mask=None, comment=None):
        self.ip_domain_id = ip_domain_id
        self.name = name
        self.ip = ip
        self.mask = mask
        self.comment = comment

    def __repr__(self):
        return '<IPv4Network %r>' % (self.name)


class IPDomain(Base):
    __tablename__ = 'ipdomain'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    comment = Column(String(1024))

    __table_args__ = (UniqueConstraint('name'),)

    @validates('name')
    def validate_name(self, key, name):
        if len(name) == 0:
            raise ValueError('IP Domain name must not be empty')
        return name

    def __init__(self, name=None, comment=None):
        self.name = name
        self.comment = comment

    def __repr__(self):
        return '<IPDomain %r>' % (self.name)


class DomainIPv4(Base):
    __tablename__ = 'domainipv4'
    id = Column(Integer, primary_key=True, nullable=False)
    ip_domain_id = Column(Integer, ForeignKey("ipdomain.id"))
    ip4_network_id = Column(Integer, ForeignKey("ipv4network.id"))

    ip_domain = relationship("IPDomain", foreign_keys=[ip_domain_id])
    ip4_network = relationship("IPv4Network", foreign_keys=[ip4_network_id])

    def __init__(self, ip_domain_id=None, ip4_network_id=None):
        self.ip_domain_id = ip_domain_id
        self.ip4_network_id = ip4_network_id

    def __repr__(self):
        return '<DomainIPv4 %r>' % (self.name)


class VLANDomain(Base):
    __tablename__ = 'vlandomain'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    comment = Column(String(1024))

    @validates('name')
    def validate_name(self, key, name):
        if len(name) == 0:
            raise ValueError('VLAN Domain name must not be empty')
        return name

    def __init__(self, name=None, comment=None):
        self.name = name
        self.comment = comment

    def __repr__(self):
        return '<VLANDomain %r>' % (self.name)


class VLAN(Base):
    __tablename__ = 'vlan'
    id = Column(Integer, primary_key=True, nullable=False)
    vlan_domain_id = Column(Integer, nullable=False)
    vlan_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    comment = Column(String(1024))

    @validates('name')
    def validate_name(self, key, name):
        if len(name) == 0:
            raise ValueError('VLAN name must not be empty')
        return name

    def __init__(self, vlan_domain_id=None, vlan_id=None, name=None, comment=None):
        self.vlan_domain_id = vlan_domain_id
        self.vlan_id = vlan_id
        self.name = name
        self.comment = comment

    def __repr__(self):
        return '<VLAN %r>' % (self.name)


class VLANIPv4(Base):
    __tablename__ = 'vlanipv4'
    id = Column(Integer, primary_key=True, nullable=False)
    vlan_domain_id = Column(Integer, nullable=False)
    vlan_id = Column(Integer, nullable=False)
    ip4_network_id = Column(Integer, nullable=False)

    @validates('name')
    def validate_name(self, key, name):
        if len(name) == 0:
            raise ValueError('VLAN name must not be empty')
        return name

    def __init__(self, vlan_domain_id=None, vlan_id=None, ip4_network_id=None):
        self.vlan_domain_id = vlan_domain_id
        self.vlan_id = vlan_id
        self.ip4_network_id = ip4_network_id

    def __repr__(self):
        return '<VLANIPv4 %r>' % (self.name)


class IPv4Address(Base):
    __tablename__ = 'ipv4address'
    id = Column(Integer, primary_key=True, nullable=False)
    ip = Column(Integer, nullable=False)
    ip_domain_id = Column(Integer, ForeignKey("ipdomain.id"))
    fqdn = Column(String(255), nullable=False)
    description = Column(String(1024))
    reserved = Column(Boolean, default=0, nullable=False)

    ip_domain = relationship("IPDomain", foreign_keys=[ip_domain_id])

    __table_args__ = (UniqueConstraint('ip_domain_id', 'ip'),)

    def __init__(self, id=None, ip=None, ip_domain_id=None, fqdn=None, description=None, reserved=None):
        self.id = id
        self.ip = ip
        self.ip_domain_id = ip_domain_id
        self.fqdn = fqdn
        self.description = description
        self.reserved = reserved

    def __repr__(self):
        return '<IPv4Address %r>' % (self.name)


"""
mysql> describe IPv4Network
    -> ;
+---------+------------------+------+-----+---------+----------------+
| Field   | Type             | Null | Key | Default | Extra          |
+---------+------------------+------+-----+---------+----------------+
| id      | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| ip      | int(10) unsigned | NO   | MUL | 0       |                |
| mask    | int(10) unsigned | NO   |     | 0       |                |
| name    | char(255)        | YES  |     | NULL    |                |
| comment | text             | YES  |     | NULL    |                |
+---------+------------------+------+-----+---------+----------------+
5 rows in set (0.00 sec)

mysql> describe IPv6Network;
+---------+------------------+------+-----+---------+----------------+
| Field   | Type             | Null | Key | Default | Extra          |
+---------+------------------+------+-----+---------+----------------+
| id      | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| ip      | binary(16)       | NO   | MUL | NULL    |                |
| mask    | int(10) unsigned | NO   |     | NULL    |                |
| last_ip | binary(16)       | NO   |     | NULL    |                |
| name    | char(255)        | YES  |     | NULL    |                |
| comment | text             | YES  |     | NULL    |                |
+---------+------------------+------+-----+---------+----------------+
6 rows in set (0.00 sec)

mysql> describe VLANDescription;
+------------+---------------------------------------+------+-----+----------+-------+
| Field      | Type                                  | Null | Key | Default  | Extra |
+------------+---------------------------------------+------+-----+----------+-------+
| domain_id  | int(10) unsigned                      | NO   | PRI | NULL     |       |
| vlan_id    | int(10) unsigned                      | NO   | PRI | 0        |       |
| vlan_type  | enum('ondemand','compulsory','alien') | NO   |     | ondemand |       |
| vlan_descr | char(255)                             | YES  |     | NULL     |       |
+------------+---------------------------------------+------+-----+----------+-------+
4 rows in set (0.00 sec)

mysql> describe VLANDomain;
+-------------+------------------+------+-----+---------+----------------+
| Field       | Type             | Null | Key | Default | Extra          |
+-------------+------------------+------+-----+---------+----------------+
| id          | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| description | char(255)        | YES  | UNI | NULL    |                |
+-------------+------------------+------+-----+---------+----------------+
2 rows in set (0.00 sec)

mysql> describe VLANIPv4;
+------------+------------------+------+-----+---------+-------+
| Field      | Type             | Null | Key | Default | Extra |
+------------+------------------+------+-----+---------+-------+
| domain_id  | int(10) unsigned | NO   | PRI | NULL    |       |
| vlan_id    | int(10) unsigned | NO   | PRI | NULL    |       |
| ipv4net_id | int(10) unsigned | NO   | PRI | NULL    |       |
+------------+------------------+------+-----+---------+-------+
3 rows in set (0.00 sec)

mysql> describe VLANIPv6;
+------------+------------------+------+-----+---------+-------+
| Field      | Type             | Null | Key | Default | Extra |
+------------+------------------+------+-----+---------+-------+
| domain_id  | int(10) unsigned | NO   | PRI | NULL    |       |
| vlan_id    | int(10) unsigned | NO   | PRI | NULL    |       |
| ipv6net_id | int(10) unsigned | NO   | PRI | NULL    |       |
+------------+------------------+------+-----+---------+-------+
3 rows in set (0.00 sec)

mysql> describe IPv4Address;
+----------+------------------+------+-----+---------+-------+
| Field    | Type             | Null | Key | Default | Extra |
+----------+------------------+------+-----+---------+-------+
| ip       | int(10) unsigned | NO   | PRI | 0       |       |
| name     | char(255)        | NO   |     |         |       |
| comment  | char(255)        | NO   |     |         |       |
| reserved | enum('yes','no') | YES  |     | NULL    |       |
+----------+------------------+------+-----+---------+-------+
4 rows in set (0.00 sec)

mysql> describe IPv6Address;
+----------+------------------+------+-----+---------+-------+
| Field    | Type             | Null | Key | Default | Extra |
+----------+------------------+------+-----+---------+-------+
| ip       | binary(16)       | NO   | PRI | NULL    |       |
| name     | char(255)        | NO   |     |         |       |
| comment  | char(255)        | NO   |     |         |       |
| reserved | enum('yes','no') | YES  |     | NULL    |       |
+----------+------------------+------+-----+---------+-------+
4 rows in set (0.00 sec)

"""


