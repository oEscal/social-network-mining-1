import React from "react";
import axios from 'axios';

import {FormInputs, CardAuthor, CardNumbers, Tweet, UserInfo, PanelHeader, LogsTable, PoliciesTableBot} from "components";
import {Nav, NavItem, NavLink, Card, CardHeader, CardBody, TabPane, TabContent, Row, Col, Badge } from 'reactstrap';

class User extends React.Component {
  state = {
    tweets: [],
    profile_data: [],
    following: [],
    followers: [],
    kibana_url: "",
    activeTab: '1',
  };
  
  constructor(props) {
    super(props);
    this.toggle = this.toggle.bind(this);
    this.anyTweets = this.anyTweets.bind(this);
    this.anyFollowers = this.anyFollowers.bind(this);
    this.anyFollowing = this.anyFollowing.bind(this);
  }

  componentDidMount() {
    const url = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1)
    this.setState({
      kibana_url: "http://192.168.85.46:5601/app/kibana#/dashboard/b10c6370-886e-11e9-9a93-576733f53835?embed=true&_g=()&_a=(description:'',filters:!(),fullScreenMode:!f,options:(hidePanelTitles:!f,useMargins:!t),panels:!((embeddableConfig:(vis:(legendOpen:!f)),gridData:(h:17,i:'1',w:16,x:0,y:7),id:'9439b220-886e-11e9-9a93-576733f53835',panelIndex:'1',type:visualization,version:'7.1.1'),(embeddableConfig:(vis:(legendOpen:!f)),gridData:(h:17,i:'3',w:16,x:32,y:7),id:a2de2780-889a-11e9-9a93-576733f53835,panelIndex:'3',type:visualization,version:'7.1.1'),(embeddableConfig:(),gridData:(h:7,i:'4',w:16,x:0,y:0),id:'2b0cac30-889b-11e9-9a93-576733f53835',panelIndex:'4',type:visualization,version:'7.1.1'),(embeddableConfig:(),gridData:(h:7,i:'5',w:16,x:32,y:0),id:'58dae640-889b-11e9-9a93-576733f53835',panelIndex:'5',type:visualization,version:'7.1.1'),(embeddableConfig:(),gridData:(h:7,i:'6',w:16,x:16,y:0),id:'852a2170-889b-11e9-9a93-576733f53835',panelIndex:'6',type:visualization,version:'7.1.1'),(embeddableConfig:(),gridData:(h:17,i:'7',w:16,x:16,y:7),id:f5d66380-889a-11e9-9a93-576733f53835,panelIndex:'7',type:visualization,version:'7.1.1')),query:(language:kuery,query:'id+:+%22"+url+"%22'),timeRestore:!f,title:'Bot+Dashboard',viewMode:view)" 
    })
    axios.get('http://192.168.85.182:5000/twitter/users/'+url)
      .then(res => {
        const profile_data = res.data[0];
        this.setState({ profile_data });
      })
    axios.get('http://192.168.85.182:5000/twitter/users/'+url+'/following')
      .then(res => {
        const following = res.data;
        this.setState({ following });
      })
    axios.get('http://192.168.85.182:5000/twitter/users/'+url+'/followers')
      .then(res => {
        const followers = res.data;
        this.setState({ followers });
      })
    axios.get('http://192.168.85.182:5000/twitter/users/'+url+'/tweets')
      .then(res => {
        const tweets = res.data;
        this.setState({ tweets });
      })
  }

  anyTweets() {
    if (this.state.tweets.length===0){
      return false
    }
    else{
      return true
    }
  }

  anyFollowing() {
    if (this.state.following.length===0){
      return false
    }
    else{
      return true
    }
  }

  anyFollowers() {
    if (this.state.followers.length===0){
      return false
    }
    else{
      return true
    }
  }
  toggle(tab) {
    if (this.state.activeTab !== tab) {
        this.setState({
            activeTab: tab
        });
    }
  }
  render() {
    return (
      <div>
        <PanelHeader
          size="sm"
        />
        <div className="content">
          <Row>
            <Col md={4} xs={12}>
              <Card className="card-user">
                <CardBody>
                  <CardAuthor
                    avatar={this.state.profile_data["profile_image_url_https"]}
                    avatarAlt="..."
                    title={this.state.profile_data["name"]}
                    description={"@"+this.state.profile_data["screen_name"]}
                  />
                  <p className="description text-center">
                    {this.state.profile_data["description"]}<br />
                  </p>
                  <p className="text-center">
                    <b>Status: </b>{this.state.profile_data["suspended"] ? "Suspended" : "Active"}<br />
                  </p>
                </CardBody>
                <hr />
                <CardNumbers
                  size="sm"
                  socials={[
                    {
                      text: "Following",
                      number:this.state.profile_data["friends_count"]
                    },
                    {
                      text: "Followers",
                      number:this.state.profile_data["followers_count"]
                    }
                  ]}
                />
              </Card>
            </Col>
            <Col md={8} xs={12}>
              <Card>
                <CardHeader>
                  <h5 className="title">Profile <Badge color="light"><i className="fab fa-1x fa-twitter"></i></Badge></h5>
                </CardHeader>
                <CardBody>
                  <form>
                    <FormInputs
                      ncols={[
                        "col-md-6 pr-1",
                        "col-md-6 px-1",
                      ]}
                      proprieties={[
                        {
                          label: "Nome",
                          inputProps: {
                            type: "text",
                            disabled: true,
                            defaultValue: this.state.profile_data["name"]
                          }
                        },
                        {
                          label: "Username",
                          inputProps: {
                            type: "text",
                            disabled: true,
                            defaultValue: this.state.profile_data["screen_name"]
                          }
                        },
                      ]}
                    />
                    <FormInputs
                      ncols={["col-md-6 pr-1", "col-md-6 pl-1"]}
                      proprieties={[
                        {
                          label: "ID",
                          inputProps: {
                            type: "number",
                            disabled: true,
                            defaultValue: this.state.profile_data["id"]
                          }
                        },
                        {
                          label: "Location",
                          inputProps: {
                            type: "text",
                            disabled: true,
                            defaultValue: this.state.profile_data["location"]
                          }
                        }
                      ]}
                    />
                    <FormInputs
                      ncols={["col-md-12"]}
                      proprieties={[
                        {
                          label: "Description",
                          inputProps: {
                            type: "textarea",
                            rows: "4",
                            cols: "80",
                            defaultValue: this.state.profile_data["description"],
                            disabled: true,
                            }
                        }
                      ]}
                    />
                  </form>
                </CardBody>
              </Card>
            </Col>
            <Col md={12} xs={12}>
              <Card className="card-plain">
                <CardHeader>
                    <Nav className="justify-content-center" tabs>
                        <NavItem>
                            <NavLink
                                className={this.state.activeTab === '1' ? 'active':''}
                                onClick={() => { this.toggle('1'); }}
                                >
                                  Statistics
                            </NavLink>
                        </NavItem>
                        <NavItem>
                            <NavLink
                                className={this.state.activeTab === '2' ? 'active':''}
                                onClick={() => { this.toggle('2'); }}
                            >
                              Replies
                            </NavLink>
                        </NavItem>
                        <NavItem>
                            <NavLink
                                className={this.state.activeTab === '3' ? 'active':''}
                                onClick={() => { this.toggle('3'); }}
                            >
                              Followers
                            </NavLink>
                        </NavItem>
                        <NavItem>
                            <NavLink
                                className={this.state.activeTab === '4' ? 'active':''}
                                onClick={() => { this.toggle('4'); }}
                            >
                              Following
                            </NavLink>
                        </NavItem>
                        <NavItem>
                            <NavLink
                                className={this.state.activeTab === '5' ? 'active':''}
                                onClick={() => { this.toggle('5'); }}
                            >
                              Policies
                            </NavLink>
                        </NavItem>
                        <NavItem>
                            <NavLink
                                className={this.state.activeTab === '6' ? 'active':''}
                                onClick={() => { this.toggle('6'); }}
                            >
                              Logs
                            </NavLink>
                        </NavItem>
                    </Nav>
                </CardHeader>
                <CardBody>
                    <TabContent activeTab={this.state.activeTab} className="text-center">
                      <TabPane tabId="1">
                        <iframe src={this.state.kibana_url} height="800" width="100%"></iframe>
                      </TabPane>
                      <TabPane tabId="2">
                        <Row>
                          {this.anyTweets()
                            ? this.state.tweets.map(tweet => 
                              <Col xs={12} md={6}>
                                <Tweet info={tweet}/>
                              </Col>
                              )
                            : <Col xs={12} md={12}>
                                <h5 className="text-muted text-center">
                                  No Tweets Available
                                </h5>
                              </Col>
                          }
                        </Row>
                      </TabPane>
                      <TabPane tabId="3">
                        <Row>
                        {this.anyFollowers()
                            ? this.state.followers.map(followers => 
                              <Col xs={12} md={6}>
                                <UserInfo userid={followers}/>
                              </Col>
                              )
                            : <Col xs={12} md={12}>
                                <h5 className="text-muted text-center">
                                  No Followers Available
                                </h5>
                              </Col>
                            }
                        </Row>
                      </TabPane>
                      <TabPane tabId="4">
                        <Row>
                          {this.anyFollowing()
                            ? this.state.following.map(following => 
                              <Col xs={12} md={6}>
                                <UserInfo userid={following}/>
                              </Col>
                              )
                            : <Col xs={12} md={12}>
                                <h5 className="text-muted text-center">
                                  Not Following Anyone
                                </h5>
                              </Col>
                            }
                        </Row>
                      </TabPane>
                      <TabPane tabId="5">
                        <PoliciesTableBot userid={ window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1)}/>
                      </TabPane>
                      <TabPane tabId="6">
                        <LogsTable userid={ window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1)}/>
                      </TabPane>
                    </TabContent>
                </CardBody>
            </Card>
            </Col>
          </Row>
        </div>
      </div>
    );
  }
}

export default User;
