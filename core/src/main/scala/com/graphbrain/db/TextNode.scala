package com.graphbrain.db

case class TextNode(override val id: String,
                    override val degree: Int = 0,
                    override val ts: Long = -1)
  extends Vertex(id, degree, ts) {

  def this(id: String, map: Map[String, String]) =
    this(id,
      map("degree").toInt,
      map("ts").toLong)

  override def extraMap = Map()

  override def setId(newId: String): Vertex = copy(id=newId)

  override def setDegree(newDegree: Int): Vertex = copy(degree=newDegree)

  override def setTs(newTs: Long): Vertex = copy(ts=newTs)

  def text = ID.lastPart(id).replace("_", " ")

  override def raw: String = {
    "type: " + "text<br />" +
    "id: " + id + "<br />"
  }
}

object TextNode {
  def fromNsAndText(namespace: String,
    text: String,
    degree: Int = 0,
    ts: Long = -1) = {

    TextNode(namespace + "/" + ID.sanitize(text).toLowerCase,
      degree,
      ts)
  }
}