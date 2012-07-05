#
## Copyright (c) rPath, Inc.
## 2012
##
## This file is distributed under the terms of the MIT License.
## A copy is available at http://www.rpath.com/permanent/mit-license.html
##

# facter plugin to allow rPath configuration XML values to be consumed by integrated Puppet

require 'rexml/document'

# recursively add smartform config to facter
# note: facter does not really support lists

def nodes(xml, position, &block)
   xml.elements.each("*/*") do |elt|
       position = "#{position}/#{elt.name}"
       children = false
       elt.elements.each { |k|
           children = true
       }
       yield position, elt.text if not children
       nodes(elt, position, &block) if children
   end
end

def process_file(path, key)

   xml = File.new(path)
   doc = REXML::Document.new(xml)

   nodes(doc,'') { |name, text|
      key = "RPATH#{name}".gsub("/","_").sub("_configuration_","_")
      Facter.add(key) do
          setcode do
             text
          end
      end
   }

end

process_file("/var/lib/rpath-tools/values.xml", "desired_properties")
process_file("/var/lib/rpath-tools/observed_values.xml", "observed_properties")

